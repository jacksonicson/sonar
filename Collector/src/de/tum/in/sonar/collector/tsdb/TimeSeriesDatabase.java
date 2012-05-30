package de.tum.in.sonar.collector.tsdb;

import java.io.IOException;
import java.util.HashSet;
import java.util.Set;

import org.apache.hadoop.hbase.HColumnDescriptor;
import org.apache.hadoop.hbase.HTableDescriptor;
import org.apache.hadoop.hbase.MasterNotRunningException;
import org.apache.hadoop.hbase.ZooKeeperConnectionException;
import org.apache.hadoop.hbase.client.HBaseAdmin;
import org.apache.hadoop.hbase.client.HTableInterface;
import org.apache.hadoop.hbase.client.HTablePool;
import org.apache.hadoop.hbase.client.Put;
import org.apache.hadoop.hbase.util.Bytes;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import de.tum.in.sonar.collector.Collector;
import de.tum.in.sonar.collector.HBaseUtil;

public class TimeSeriesDatabase {

	private static Logger logger = LoggerFactory.getLogger(Collector.class);

	private HBaseUtil hbaseUtil;

	private IdResolver labelResolver;
	private IdResolver hostnameResolver;
	private IdResolver sensorResolver;

	private HTablePool tsdbTablePool;

	public TimeSeriesDatabase() {
		this.labelResolver = new IdResolver("label");
		this.hostnameResolver = new IdResolver("hostname");
		this.sensorResolver = new IdResolver("sensor");

		this.tsdbTablePool = new HTablePool();
	}

	private int appendToKey(byte[] key, int index, long value) {
		return appendToKey(key, index, Bytes.toBytes(value));
	}

	private int appendToKey(byte[] key, int index, byte[] value) {
		System.arraycopy(value, 0, key, index, value.length);
		return value.length;
	}

	byte[] buildKey(DataPoint point) throws UnresolvableException {

		sensorResolver.setHbaseUtil(hbaseUtil);
		hostnameResolver.setHbaseUtil(hbaseUtil);
		labelResolver.setHbaseUtil(hbaseUtil);

		int keyWidth = Const.SENSOR_ID_WIDTH + Const.TIMESTAMP_WIDTH + Const.HOSTNAME_WIDTH + Const.LABEL_ID_WIDTH
				* point.getLabels().size();
		byte[] key = new byte[keyWidth];

		int index = 0;
		index += appendToKey(key, index, sensorResolver.resolveName(point.getSensor()));
		index += appendToKey(key, index, point.getHourSinceEpoch());
		index += appendToKey(key, index, hostnameResolver.resolveName(point.getHostname()));

		for (String label : point.getLabels()) {
			index += appendToKey(key, index, labelResolver.resolveName(label));
		}

		return key;
	}

	public void setupTables() throws TableCreationException {

		try {
			HBaseAdmin hbase = new HBaseAdmin(hbaseUtil.getConfig());

			// Table layout
			Set<InternalTableDescriptor> tables = new HashSet<InternalTableDescriptor>();
			tables.add(new InternalTableDescriptor(Const.TABLE_TSDB, new String[] { Const.FAMILY_TSDB_DATA }));
			tables.add(new InternalTableDescriptor(Const.FAMILY_TSDB_DATA, new String[] { Const.FAMILY_UID_FORWARD,
					Const.FAMILY_UID_BACKWARD }));

			// Remove all existing table from the set
			HTableDescriptor tableDescriptors[] = hbase.listTables();
			for (HTableDescriptor desc : tableDescriptors) {
				String name = Bytes.toString(desc.getName());
				tables.remove(new InternalTableDescriptor(name, new String[] {}));

				logger.info("HBase table found: " + name);
			}

			// Create all remaining tables
			for (InternalTableDescriptor internalDesc : tables) {

				logger.debug("Creating HBase table: " + internalDesc.getName());

				HTableDescriptor desc = new HTableDescriptor(internalDesc.getName());
				for (String family : internalDesc.getFamilies()) {
					HColumnDescriptor meta = new HColumnDescriptor(family.getBytes());
					desc.addFamily(meta);
				}

				hbase.createTable(desc);
			}

		} catch (MasterNotRunningException e) {
			throw new TableCreationException(e);
		} catch (ZooKeeperConnectionException e) {
			throw new TableCreationException(e);
		} catch (IOException e) {
			throw new TableCreationException(e);
		}
	}

	private void scheduleCompaction(byte[] row) {
		// TODO: Add row to compaction algorithm
	}

	public void writeData(DataPoint dataPoint) {

		try {
			byte[] key = buildKey(dataPoint);

			HTableInterface table = this.tsdbTablePool.getTable(Const.TABLE_TSDB);

			// Create a new row in this case
			Put put = new Put(key);
			byte[] secs = Bytes.toBytes(dataPoint.getSecondsInHour());
			byte[] value = Bytes.toBytes(dataPoint.getValue());

			put.add(Bytes.toBytes(Const.FAMILY_TSDB_DATA), secs, value);
			table.put(put);

			scheduleCompaction(key);

		} catch (IOException e) {
			logger.error("could not write tsdb to hbase", e);
		} catch (UnresolvableException e) {
			logger.error("could not create key for datapoint", e);
		}

		logger.info("writing data ");
	}

	public void setHbaseUtil(HBaseUtil hbaseUtil) {
		this.hbaseUtil = hbaseUtil;
	}

}
