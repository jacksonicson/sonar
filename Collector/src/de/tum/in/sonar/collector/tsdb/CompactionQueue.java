package de.tum.in.sonar.collector.tsdb;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.NavigableMap;
import java.util.concurrent.DelayQueue;

import org.apache.hadoop.hbase.client.Delete;
import org.apache.hadoop.hbase.client.Get;
import org.apache.hadoop.hbase.client.HTable;
import org.apache.hadoop.hbase.client.Put;
import org.apache.hadoop.hbase.client.Result;
import org.apache.hadoop.hbase.util.Bytes;
import org.apache.thrift.TDeserializer;
import org.apache.thrift.TException;
import org.apache.thrift.TSerializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import de.tum.in.sonar.collector.HBaseUtil;
import de.tum.in.sonar.collector.tsdb.gen.CompactPoint;
import de.tum.in.sonar.collector.tsdb.gen.CompactTimeseries;

class CompactionQueue extends Thread {

	// Logger
	private Logger logger = LoggerFactory.getLogger(CompactionQueue.class);

	private static final boolean COMPACTION_ENABLED = false;

	private static final long TIME_DELAY = 10 * 60;

	private DelayQueue<RowKeyJob> delayQueue = new DelayQueue<RowKeyJob>();

	private HTable table = null;

	public void schedule(byte[] key) {
		if (!COMPACTION_ENABLED)
			return;

		RowKeyJob rowKeyJob = new RowKeyJob(TIME_DELAY, key);
		if (delayQueue.contains(rowKeyJob)) {
			logger.trace("Removing: " + key);
			delayQueue.remove(rowKeyJob);
		}

		logger.trace("Adding: " + key);
		delayQueue.add(rowKeyJob);
		logger.trace("length: " + delayQueue.size());
	}

	private void compact(byte[] key, NavigableMap<byte[], byte[]> familyMap) throws IOException, TException,
			InterruptedException {
		List<CompactPoint> points = new ArrayList<CompactPoint>();
		Delete del = new Delete(key);

		CompactTimeseries ts = null;
		TSerializer serializer = new TSerializer();
		TDeserializer deserializer = new TDeserializer();

		for (byte[] quali : familyMap.keySet()) {
			if (Bytes.toString(quali).equals("data")) {
				logger.info("Deserializing...");
				byte[] data = familyMap.get(quali);
				ts = new CompactTimeseries();
				deserializer.deserialize(ts, data);
				continue;
			}

			CompactPoint point = new CompactPoint();
			points.add(point);
			point.setTimestamp(Bytes.toLong(quali));
			point.setValue(Bytes.toDouble(familyMap.get(quali)));

			// Delete the point from the row
			del.deleteColumns(Bytes.toBytes(Const.FAMILY_TSDB_DATA), quali);
		}

		if (ts == null)
			ts = new CompactTimeseries();

		for (CompactPoint element : points)
			ts.addToPoints(element);

		byte[] buffer = serializer.serialize(ts);

		// Updating HBase
		// The delete and push operations do not run in a transaction. Therefore, it is possible
		// that some points are stored twice, once in the compaction and once in a cell. The
		// data will then be compacted again and the compaction will contain two points with the
		// same qualifier. This will be detected in the decompaction phase!
		Put put = new Put(key);
		put.add(Bytes.toBytes(Const.FAMILY_TSDB_DATA), Bytes.toBytes("data"), buffer);
		table.put(put);
		table.delete(del);
		table.flushCommits();
	}

	private void compact(List<byte[]> keys) throws IOException, TException, InterruptedException {
		logger.info("running compaction of " + keys.size() + " rows ...");

		List<Get> gets = new ArrayList<Get>();
		for (byte[] key : keys) {
			Get get = new Get(key);
			gets.add(get);
		}

		Result[] results = table.get(gets);
		for (int i = 0; i < results.length; i++) {
			Result result = results[i];
			NavigableMap<byte[], byte[]> familyMap = result.getFamilyMap(Bytes.toBytes(Const.FAMILY_TSDB_DATA));
			try {
				compact(keys.get(i), familyMap);
			} catch (IOException e) {
				continue;
			} catch (TException e) {
				continue;
			} catch (InterruptedException e) {
				continue;
			}
		}

		logger.info("Compaction finished");
	}

	private boolean getCompactionCell(final byte[] row) throws IOException {
		Get get = new Get(row);
		get.addColumn(Bytes.toBytes(Const.FAMILY_TSDB_DATA), Bytes.toBytes("data"));
		Result result = table.get(get);
		return !result.isEmpty();
	}

	private long getLastModified(final byte[] row) throws IOException {
		Get get = new Get(row);
		get.addFamily(Bytes.toBytes("data"));
		Result result = table.get(get);

		List<Long> timestampList = new ArrayList<Long>();
		Map<Long, byte[]> timestamps = result.getMap().get(Bytes.toBytes(Const.FAMILY_TSDB_DATA)).get(
				Bytes.toBytes("data"));
		timestampList.addAll(timestamps.keySet());

		Collections.sort(timestampList);
		long maxTimestamp = timestampList.get(timestampList.size() - 1);

		return maxTimestamp;
	}

	@Override
	public void run() {
		logger.info("Starting compaction thread...");

		List<byte[]> compacts = new ArrayList<byte[]>();
		while (true) {
			try {
				RowKeyJob data = delayQueue.take();

				// Compaction cell does not exist
				boolean exists = getCompactionCell(data.getRowKey());
				if (exists == false) {
					compacts.add(data.getRowKey());
				} else {
					// Check age of the last insert (compaction or TSD value)
					long timestamp = getLastModified(data.getRowKey());
					long delta = System.currentTimeMillis() - timestamp;
					if (delta > TIME_DELAY) {
						// Compaction
						compacts.add(data.getRowKey());
					} else {
						// Reschedule
						logger.debug("reschedule compaction because compaction field changed: " + data.getRowKey());
						schedule(data.getRowKey());
					}
				}

				// Finally trigger compaction
				if (compacts.size() > 20) {
					compact(compacts);
					compacts.clear();
				}

			} catch (IOException e) {
				logger.error("Error while compacting", e);
			} catch (TException e) {
				logger.error("Error while compacting", e);
			} catch (InterruptedException e) {
				logger.error("Error while compacting", e);
			}

			// Rate limit compaction
			try {
				Thread.sleep(3000);
			} catch (InterruptedException e) {
				// pass
			}
		}
	}

	void setHbaseUtil(HBaseUtil hbaseUtil) {
		try {
			table = new HTable(hbaseUtil.getConfig(), Const.TABLE_TSDB);
			table.setAutoFlush(false);
		} catch (IOException e) {
			logger.error("could not open HBase table", e);
		}
	}
}
