package de.tum.in.sonar.collector.tsdb;

import java.io.IOException;
import java.util.HashSet;
import java.util.NavigableMap;
import java.util.Set;

import org.apache.hadoop.hbase.HColumnDescriptor;
import org.apache.hadoop.hbase.HTableDescriptor;
import org.apache.hadoop.hbase.MasterNotRunningException;
import org.apache.hadoop.hbase.ZooKeeperConnectionException;
import org.apache.hadoop.hbase.client.HBaseAdmin;
import org.apache.hadoop.hbase.client.HTableInterface;
import org.apache.hadoop.hbase.client.HTablePool;
import org.apache.hadoop.hbase.client.Put;
import org.apache.hadoop.hbase.client.Result;
import org.apache.hadoop.hbase.client.ResultScanner;
import org.apache.hadoop.hbase.client.Scan;
import org.apache.hadoop.hbase.util.Bytes;
import org.apache.thrift.TException;
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

	private CompactionQueue compactionQueue;

	public TimeSeriesDatabase() {
		this.labelResolver = new IdResolver("label");
		this.hostnameResolver = new IdResolver("hostname");
		this.sensorResolver = new IdResolver("sensor");

		this.tsdbTablePool = new HTablePool();

		this.compactionQueue = new CompactionQueue();
		this.compactionQueue.start();
	}

	private int appendToKey(byte[] key, int index, long value) {
		return appendToKey(key, index, Bytes.toBytes(value));
	}

	private int appendToKey(byte[] key, int index, byte[] value) {
		System.arraycopy(value, 0, key, index, value.length);
		return value.length;
	}

	private int keyWidth(int labels) {
		int keyWidth = Const.SENSOR_ID_WIDTH + Const.TIMESTAMP_WIDTH + Const.HOSTNAME_WIDTH + Const.LABEL_ID_WIDTH
				* labels;

		return keyWidth;
	}

	byte[] buildKey(MetricPoint point) throws UnresolvableException {

		int keyWidth = keyWidth(point.getLabels().size());
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
			Set<InternalTableSchema> tables = new HashSet<InternalTableSchema>();
			tables.add(new InternalTableSchema(Const.TABLE_TSDB, new String[] { "forward", "backward" }));
			tables.add(new InternalTableSchema(Const.TABLE_UID, new String[] { Const.FAMILY_TSDB_DATA }));
			tables.add(new InternalTableSchema(Const.FAMILY_TSDB_DATA, new String[] { Const.FAMILY_UID_FORWARD,
					Const.FAMILY_UID_BACKWARD }));

			// Remove all existing table from the set
			HTableDescriptor tableDescriptors[] = hbase.listTables();
			for (HTableDescriptor desc : tableDescriptors) {
				String name = Bytes.toString(desc.getName());
				tables.remove(new InternalTableSchema(name, new String[] {}));

				logger.info("HBase table found: " + name);
			}

			// Create all remaining tables
			for (InternalTableSchema internalDesc : tables) {

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
		this.compactionQueue.schedule(row);
	}

	public void writeData(MetricPoint dataPoint) {

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

		this.sensorResolver.setHbaseUtil(hbaseUtil);
		this.hostnameResolver.setHbaseUtil(hbaseUtil);
		this.labelResolver.setHbaseUtil(hbaseUtil);

		this.compactionQueue.setHbaseUtil(hbaseUtil);
	}

	long getHourSinceEpoch(long timestamp) {
		long hourSinceEpoch = timestamp - (timestamp % 3600);
		return hourSinceEpoch;
	}

	long getSecondsInHour(long timestamp) {
		long hourSinceEpoch = getHourSinceEpoch(timestamp);
		long offset = (timestamp - hourSinceEpoch);
		return offset;
	}

	public TimeSeries run(Query query) throws QueryException, UnresolvableException {

		try {
			logger.debug("start: " + query.getStartTime());
			logger.debug("stop: " + query.getStopTime());
			logger.debug("hostname: " + query.getHostname());
			logger.debug("sensor: " + query.getSensor());

			HTableInterface table = this.tsdbTablePool.getTable(Const.TABLE_TSDB);
			Scan scan = new Scan();

			// Start row
			byte[] startRow = new byte[keyWidth(query.getLabels().size())];
			int index = 0;
			index += appendToKey(startRow, index, Bytes.toBytes(sensorResolver.resolveName(query.getSensor())));
			index += appendToKey(startRow, index, getHourSinceEpoch(query.getStartTime()));

			if (query.getHostname() != null)
				index += appendToKey(startRow, index, Bytes.toBytes(hostnameResolver.resolveName(query.getHostname())));
			else
				index += Const.HOSTNAME_WIDTH;

			scan.setStartRow(startRow);

			// Stop row
			byte[] stopRow = new byte[keyWidth(query.getLabels().size())];

			index = 0;
			index += appendToKey(stopRow, index, Bytes.toBytes(sensorResolver.resolveName(query.getSensor())));
			index += appendToKey(stopRow, index, getHourSinceEpoch(query.getStopTime()));

			if (query.getHostname() != null)
				index += appendToKey(stopRow, index, Bytes.toBytes(hostnameResolver.resolveName(query.getHostname())));

			for (; index < stopRow.length; index++)
				stopRow[index] = (byte) 0xFF;

			scan.setStopRow(stopRow);

			// Load the scanner
			logger.debug("Starting table scanner on query");
			ResultScanner scanner = table.getScanner(scan);

			TimeSeries timeSeries = new TimeSeries();

			Result next;
			while ((next = scanner.next()) != null) {

				logger.debug("Row found");

				byte[] rowKey = next.getRow();
				long timestampHours = Bytes.toLong(rowKey, Const.SENSOR_ID_WIDTH);

				TimeSeriesFragment fragment = timeSeries.newFragment();

				NavigableMap<byte[], byte[]> familyMap = next.getFamilyMap(Bytes.toBytes(Const.FAMILY_TSDB_DATA));

				for (byte[] key : familyMap.keySet()) {

					if (Bytes.toString(key).equals("data")) {
						try {
							fragment.addSegment(timestampHours, familyMap.get(key));
						} catch (TException e) {
							e.printStackTrace();
						}
						continue;
					}

					long value = Bytes.toLong(key);
					long data = Bytes.toLong(familyMap.get(key));

					TimeSeriesPoint p = new TimeSeriesPoint();
					p.setTimestamp(timestampHours + value);
					p.setValue(data);
					fragment.addPoint(p);

					logger.info("qualifier: " + value + " data: " + data);
				}
			}

			return timeSeries;

		} catch (IOException e) {
			throw new QueryException(e);
		}
	}
}
