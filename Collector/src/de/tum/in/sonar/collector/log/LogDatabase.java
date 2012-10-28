package de.tum.in.sonar.collector.log;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.NavigableMap;

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
import org.apache.thrift.TDeserializer;
import org.apache.thrift.TException;
import org.apache.thrift.TSerializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import de.tum.in.sonar.collector.HBaseUtil;
import de.tum.in.sonar.collector.Identifier;
import de.tum.in.sonar.collector.LogMessage;
import de.tum.in.sonar.collector.LogsQuery;
import de.tum.in.sonar.collector.tsdb.IdResolver;
import de.tum.in.sonar.collector.tsdb.InvalidLabelException;
import de.tum.in.sonar.collector.tsdb.QueryException;
import de.tum.in.sonar.collector.tsdb.TableCreationException;
import de.tum.in.sonar.collector.tsdb.UnresolvableException;

public class LogDatabase {

	private static Logger logger = LoggerFactory.getLogger(LogDatabase.class);

	private HBaseUtil hbaseUtil;
	private HTablePool tablePool;

	private IdResolver labelResolver;
	private IdResolver hostnameResolver;
	private IdResolver sensorResolver;

	private long internalCounter = 0;

	public LogDatabase() {
		this.labelResolver = new IdResolver("label");
		this.hostnameResolver = new IdResolver("hostname");
		this.sensorResolver = new IdResolver("sensor");

		this.tablePool = new HTablePool();
	}

	public void setHbaseUtil(HBaseUtil hbaseUtil) {
		this.hbaseUtil = hbaseUtil;
		this.sensorResolver.setHbaseUtil(hbaseUtil);
		this.hostnameResolver.setHbaseUtil(hbaseUtil);
		this.labelResolver.setHbaseUtil(hbaseUtil);
	}

	private int keyWidth() {
		int keyWidth = LogConstants.SENSOR_ID_WIDTH + LogConstants.HOSTNAME_WIDTH + LogConstants.TIMESTAMP_WIDTH;
		return keyWidth;
	}

	private int appendToKey(byte[] key, int index, long value) {
		return appendToKey(key, index, Bytes.toBytes(value));
	}

	private int appendToKey(byte[] key, int index, byte[] value) {
		System.arraycopy(value, 0, key, index, value.length);
		return value.length;
	}

	private byte[] buildKey(Identifier id) throws UnresolvableException, InvalidLabelException {
		int keyWidth = keyWidth();
		byte[] key = new byte[keyWidth];

		int index = 0;
		index += appendToKey(key, index, sensorResolver.resolveName(id.getSensor()));
		index += appendToKey(key, index, hostnameResolver.resolveName(id.getHostname()));
		index += appendToKey(key, index, id.getTimestamp());

		return key;
	}

	public void writeData(Identifier id, LogMessage message) {
		try {
			byte[] key = buildKey(id);
			HTableInterface table = this.tablePool.getTable(LogConstants.TABLE_LOG);

			// Create a new row in this case
			// TODO: Why is this?
			if (message.getTimestamp() == 0)
				message.setTimestamp(id.getTimestamp());

			TSerializer serializer = new TSerializer();

			// Hack - if this is not applied log messages with the same timestamp overwrite each other!
			internalCounter++;

			Put put = new Put(key);
			// TODO: Why does the qualifier need a the hostname?
			put.add(Bytes.toBytes(LogConstants.FAMILY_LOG_DATA), Bytes.toBytes(id.getHostname() + internalCounter), serializer.serialize(message));
			table.put(put);

		} catch (IOException e) {
			logger.error("could not write tsdb to hbase", e);
		} catch (UnresolvableException e) {
			logger.error("could not create key for datapoint", e);
		} catch (TException e) {
			logger.error("could not serialize payload data", e);
		} catch (InvalidLabelException e) {
			logger.error("invalid label used", e);
		}
	}

	public List<LogMessage> run(LogsQuery logQuery) throws QueryException, UnresolvableException, InvalidLabelException {
		List<LogMessage> logMessages = null;
		try {
			
			// determine if start range and end range of log priority is
			// provided
			boolean logPriorityFlag = false;
			if (-1 != logQuery.getLogStartRange() && -1 != logQuery.getLogEndRange()) {
				logPriorityFlag = true;
			}

			HTableInterface table = this.tablePool.getTable(LogConstants.TABLE_LOG);
			Scan scan = new Scan();
			scan.setCaching(100);

			// set the range

			byte[] startRow = new byte[keyWidth()];
			int index = 0;
			index += appendToKey(startRow, index, Bytes.toBytes(sensorResolver.resolveName(logQuery.getSensor())));
			index += appendToKey(startRow, index, Bytes.toBytes(hostnameResolver.resolveName(logQuery.getHostname())));
			index += appendToKey(startRow, index, logQuery.getStartTime());
			scan.setStartRow(startRow);

			byte[] endRow = new byte[keyWidth()];
			index = 0;
			index += appendToKey(endRow, index, Bytes.toBytes(sensorResolver.resolveName(logQuery.getSensor())));
			index += appendToKey(endRow, index, Bytes.toBytes(hostnameResolver.resolveName(logQuery.getHostname())));
			index += appendToKey(endRow, index, logQuery.getStopTime());
			scan.setStopRow(endRow);

			ResultScanner scanner = table.getScanner(scan);

			logMessages = new ArrayList<LogMessage>();

			Result next;
			while ((next = scanner.next()) != null) {

				NavigableMap<byte[], byte[]> familyMap = next.getFamilyMap(Bytes.toBytes(LogConstants.FAMILY_LOG_DATA));

				for (byte[] qualifier : familyMap.keySet()) {
					byte[] data = familyMap.get(qualifier);
					if (data == null)
						continue;

					// TODO: The instance is created for each row. Is this necessary?
					TDeserializer deserializer = new TDeserializer();
					LogMessage logMsg = new LogMessage();
					try {
						deserializer.deserialize(logMsg, data);
						if (logPriorityFlag) {
							// if log priority is specified
							if (logQuery.getLogStartRange() >= logMsg.getLogLevel()
									|| logQuery.getLogEndRange() <= logMsg.getLogLevel()) {
								// add only when the log message range matches
								// that of the current log level
								logMessages.add(logMsg);
							}
						} else {
							// add messages when log priority range is not
							// specified
							logMessages.add(logMsg);
						}
					} catch (TException e) {
						continue;
					}
				}
			}
		} catch (IOException e) {
			throw new QueryException(e);
		}
		return logMessages;
	}

	public void setupTables() throws TableCreationException {
		HBaseAdmin hbase = null;
		try {
			logger.info("Setting up Log table..");
			hbase = new HBaseAdmin(hbaseUtil.getConfig());
			boolean tableExists = false;

			// check if the log table already exists
			// if it exists, do not create the table
			HTableDescriptor tableDescriptors[] = hbase.listTables();
			for (HTableDescriptor desc : tableDescriptors) {
				String name = Bytes.toString(desc.getName());
				if (name.equalsIgnoreCase(LogConstants.TABLE_LOG)) {
					logger.info("Log table " + name + " already exists");
					tableExists = true;
					break;
				}
			}
			if (!tableExists) {
				// Create all remaining tables
				logger.info("Creating Log table..");
				HTableDescriptor desc = new HTableDescriptor(LogConstants.TABLE_LOG);
				HColumnDescriptor meta = new HColumnDescriptor(Bytes.toBytes(LogConstants.FAMILY_LOG_DATA));
				desc.addFamily(meta);
				hbase.createTable(desc);
			}
		} catch (MasterNotRunningException e) {
			throw new TableCreationException(e);
		} catch (ZooKeeperConnectionException e) {
			throw new TableCreationException(e);
		} catch (IOException e) {
			throw new TableCreationException(e);
		} finally {
			if (hbase != null) {
				try {
					hbase.close();
				} catch (IOException e) {
					logger.trace("Error while closing hbase connection", e);
				}
			}
		}
	}
}
