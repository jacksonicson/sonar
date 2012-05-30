package de.tum.in.sonar.collector.tsdb;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.NavigableMap;
import java.util.Vector;

import org.apache.hadoop.hbase.client.Delete;
import org.apache.hadoop.hbase.client.Get;
import org.apache.hadoop.hbase.client.HTable;
import org.apache.hadoop.hbase.client.Put;
import org.apache.hadoop.hbase.client.Result;
import org.apache.hadoop.hbase.util.Bytes;
import org.apache.thrift.TException;
import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.protocol.TProtocol;
import org.apache.thrift.transport.TMemoryBuffer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import de.tum.in.sonar.collector.HBaseUtil;
import de.tum.in.sonar.collector.tsdb.gen.CompactPoint;
import de.tum.in.sonar.collector.tsdb.gen.CompactTimeseries;

class CompactionQueue extends Thread {

	private Logger logger = LoggerFactory.getLogger(CompactionQueue.class);

	private List<byte[]> scheduledRows = new Vector<byte[]>();

	private HBaseUtil hbaseUtil;

	private HTable table = null;

	public CompactionQueue() {
		this.start();
	}

	void schedule(byte[] key) {
		synchronized (scheduledRows) {
			this.scheduledRows.add(key);
			this.scheduledRows.notify();
		}
	}

	private void compact(byte[] key) throws IOException, TException {
		if (table == null) {
			table = new HTable(hbaseUtil.getConfig(), Const.TABLE_TSDB);
		}

		Get get = new Get(key);
		Result result = table.get(get);
		NavigableMap<byte[], byte[]> familyMap = result.getFamilyMap(Bytes.toBytes(Const.FAMILY_TSDB_DATA));

		List<CompactPoint> points = new ArrayList<CompactPoint>();
		List<Delete> deletes = new ArrayList<Delete>();

		// http://diwakergupta.github.com/thrift-missing-guide/thrift.pdf
		TMemoryBuffer buffer = new TMemoryBuffer(32);
		TProtocol protocol = new TBinaryProtocol(buffer);
		CompactTimeseries ts = null;

		for (byte[] quali : familyMap.keySet()) {
			if (Bytes.toString(quali).equals("data")) {

				byte[] data = familyMap.get(quali);
				buffer.read(data, 0, data.length);
				ts = new CompactTimeseries();
				ts.read(protocol);

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

		buffer = new TMemoryBuffer(32);
		protocol = new TBinaryProtocol(buffer);
		ts.write(protocol);

		// Updating HBase
		Put put = new Put();
		put.add(Bytes.toBytes(Const.FAMILY_TSDB_DATA), Bytes.toBytes("data"), buffer.getArray());
		table.put(put);
		table.delete(deletes);
	}

	public void run() {

		while (true) {

			byte[] key = null;

			synchronized (scheduledRows) {
				if (scheduledRows.isEmpty()) {
					try {
						scheduledRows.wait();
					} catch (InterruptedException e) {
						e.printStackTrace();
						continue;
					}
				}

				key = scheduledRows.get(0);
				scheduledRows.remove(0);
			}

			try {
				compact(key);
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
