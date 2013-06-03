package de.tum.in.sonar.collector.log;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.NavigableMap;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;

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

public class LogDatabase extends Thread {

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

		this.start();
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

	class Job {
		Identifier id;
		LogMessage message;

		public Job(Identifier id, LogMessage message) {
			this.id = id;
			this.message = message;
		}
	}

	private BlockingQueue<Job> queue = new LinkedBlockingQueue<Job>();

	public void run() {
		while (true) {
			try {
				Job job = queue.take();

				if(queue.size() > 300)
					logger.warn("Log queue size is: " + queue.size());
				
				try {
					byte[] key = buildKey(job.id);
					HTableInterface table = this.tablePool.getTable(LogConstants.TABLE_LOG);

					// Ensure that a timestamp is given
					if (job.message.getTimestamp() == 0)
						job.message.setTimestamp(job.id.getTimestamp());

					TSerializer serializer = new TSerializer();

					// Update internal message counter
					if (internalCounter++ > Integer.MAX_VALUE)
						internalCounter = 0;

					// The hostname plus the internalCounter guarantee that the column name is unique
					// even if multiple systems are writing to the same log sensor (should be impossible)
					Put put = new Put(key);
					put.add(Bytes.toBytes(LogConstants.FAMILY_LOG_DATA), Bytes.toBytes(job.id.getHostname()
							+ internalCounter), serializer.serialize(job.message));
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
			} catch (InterruptedException e) {
				logger.error("error while taking item from queue", e);
			}
		}
	}

	public void writeData(Identifier id, LogMessage message) {
		try {
			this.queue.put(new Job(id, message));
		} catch (InterruptedException e) {
			logger.error("error while putting item in queue", e);
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

			// Scanner on the table
			ResultScanner scanner = table.getScanner(scan);

			// Results
			logMessages = new ArrayList<LogMessage>();

			// Deserializer for the log data
			TDeserializer deserializer = new TDeserializer();

			// Iterate over all rows
			Result next;
			while ((next = scanner.next()) != null) {

				// Navigator on column family
				NavigableMap<byte[], byte[]> familyMap = next.getFamilyMap(Bytes.toBytes(LogConstants.FAMILY_LOG_DATA));

				// Iterate over all qualifiers. Each one contains a log message
				for (byte[] qualifier : familyMap.keySet()) {
					byte[] data = familyMap.get(qualifier);
					if (data == null)
						continue;

					// Create a new log message by deserializing the HBase content
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
