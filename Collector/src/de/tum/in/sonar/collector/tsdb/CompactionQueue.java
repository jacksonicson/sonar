package de.tum.in.sonar.collector.tsdb;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.NavigableMap;
import java.util.concurrent.DelayQueue;

import org.apache.hadoop.hbase.KeyValue;
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

	// the delay time 30 minutes currently
	private static final long QUEUE_TIME_DELAY = 1800000L;

	private Logger logger = LoggerFactory.getLogger(CompactionQueue.class);

	private DelayQueue<RowKeyJob> dq = new DelayQueue<RowKeyJob>();

	private RowKeyJob data;

	private HBaseUtil hbaseUtil;

	private HTable table = null;

	/**
	 * Schedule the row for compaction
	 * 
	 * @param key
	 *            The row key
	 */
	public void schedule(byte[] key) {
		logger.info("Scheduling:" + dq.size());
		synchronized (this) {
			// check if the data already exists
			// if it does, update the delay and the addition timestamp
			RowKeyJob rowKeyJob = new RowKeyJob(QUEUE_TIME_DELAY, key,
					System.currentTimeMillis());
			if (dq.contains(rowKeyJob)) {
				logger.debug("Rowkey already scheduled for compaction.. rescheduling");
				dq.remove(rowKeyJob);
			}
			dq.add(rowKeyJob);
		}
	}

	/**
	 * Compact the row
	 * 
	 * @param key
	 * @param timestamp
	 * @throws IOException
	 * @throws TException
	 * @throws InterruptedException
	 */
	private void compact(byte[] key) throws IOException, TException,
			InterruptedException {
		if (table == null) {
			table = new HTable(hbaseUtil.getConfig(), Const.TABLE_TSDB);
		}
		Get get = new Get(key);
		Result result = table.get(get);
		NavigableMap<byte[], byte[]> familyMap = result.getFamilyMap(Bytes
				.toBytes(Const.FAMILY_TSDB_DATA));

		List<CompactPoint> points = new ArrayList<CompactPoint>();
		List<Delete> deletes = new ArrayList<Delete>();

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
			point.setValue(Bytes.toLong(familyMap.get(quali)));

			Delete del = new Delete(key);
			del.deleteColumn(Bytes.toBytes(Const.FAMILY_TSDB_DATA), quali);
			deletes.add(del);
		}

		if (ts == null)
			ts = new CompactTimeseries();

		for (CompactPoint element : points)
			ts.addToPoints(element);

		byte[] buffer = serializer.serialize(ts);

		// Updating HBase
		Put put = new Put(key);
		put.add(Bytes.toBytes(Const.FAMILY_TSDB_DATA), Bytes.toBytes("data"),
				buffer);
		table.put(put);
		table.delete(deletes);
		table.flushCommits();
	}

	private long getLastModified(byte[] row) {
		if (table == null) {
			try {
				table = new HTable(hbaseUtil.getConfig(), Const.TABLE_TSDB);
			} catch (IOException e) {
				e.printStackTrace();
			}
		}
		Get get = new Get(row);
		Result result;
		try {
			result = table.get(get);
			NavigableMap<byte[], byte[]> familyMap = result.getFamilyMap(Bytes
					.toBytes(Const.FAMILY_TSDB_DATA));
			System.out.println(familyMap.size());

			KeyValue keyValues = result.getColumnLatest(
					Bytes.toBytes(Const.FAMILY_TSDB_DATA),
					Bytes.toBytes(Const.FAMILY_TSDB_DATA));
			if (null == keyValues) {
				return 0L;
			}
			return keyValues.getTimestamp();
		} catch (IOException e) {
			e.printStackTrace();
		}
		return 0L;
	}

	@Override
	public void run() {
		logger.info("Started the compaction queue");
		long dequeueTime = 0;
		while (true) {
			try {
				data = (RowKeyJob) dq.take();
				dequeueTime = System.currentTimeMillis();
			} catch (InterruptedException e1) {
				e1.printStackTrace();
			}

			byte[] rowKey = data.getRowKey();

			// check the last modified timestamp on the compacted row
			long time = getLastModified(rowKey);

			try {
				if (time == 0L) {
					// when there was no previous compaction done i.e no
					// compacted row.
					// Do the compaction
					logger.info("Running compaction as compaction was not run previously..");
					compact(rowKey);
				} else if (dequeueTime - time < QUEUE_TIME_DELAY) {
					// compaction was done previously but it was done less than
					// QUEUE_TIME_DELAY time ago
					// re-schedule compaction
					logger.info("Rescheduling compaction for later run as it was run recently..");
					schedule(rowKey);
				} else {
					// run the compaction
					logger.info("Running compaction..");
					compact(rowKey);
				}
			} catch (InterruptedException e) {
				e.printStackTrace();
			} catch (IOException e) {
				e.printStackTrace();
			} catch (TException e) {
				e.printStackTrace();
			}
		}
	}

	void setHbaseUtil(HBaseUtil hbaseUtil) {
		this.hbaseUtil = hbaseUtil;
	}
}
