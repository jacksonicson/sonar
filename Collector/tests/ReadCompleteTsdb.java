import java.io.IOException;
import java.util.NavigableMap;

import org.apache.hadoop.hbase.client.Get;
import org.apache.hadoop.hbase.client.HTable;
import org.apache.hadoop.hbase.client.Result;
import org.apache.hadoop.hbase.client.ResultScanner;
import org.apache.hadoop.hbase.client.Scan;
import org.apache.hadoop.hbase.util.Bytes;

import de.tum.in.sonar.collector.HBaseUtil;

public class ReadCompleteTsdb {

	public ReadCompleteTsdb() throws IOException {

		HBaseUtil util = new HBaseUtil();

		HTable table = new HTable(util.getConfig(), "tsdb");
		

		Scan scan = new Scan();

		
		
		System.out.println("Scanning over the rows:");
		ResultScanner scanner = table.getScanner(scan);
		for (Result res : scanner) {
			System.out.println("Row: " + res.getRow());

			byte[] key = res.getRow();

			long sensorId = Bytes.toLong(key, 0);
			System.out.println("Sensor: " + sensorId);

			long timestamp = Bytes.toLong(key, 8);
			System.out.println("Timestamp: " + timestamp);

			long hostnameId = Bytes.toLong(key, 16);
			System.out.println("Hostname: " + hostnameId);

			// All the tags
			System.out.println("Reading tags: ");
			int offset = 24;
			while (offset < key.length) {
				long tagId = Bytes.toLong(key, offset);
				System.out.println("Tag id: " + tagId);
				offset += 8;
			}

			NavigableMap<byte[], byte[]> map = res.getFamilyMap(Bytes.toBytes("data"));
			for (byte[] k : map.keySet()) {
				System.out.println("KEY:" + Bytes.toLong(k));
				
				Get get = new Get(res.getRow());
				get.setMaxVersions(100);
				Result tres = table.get(get);
				
				for (long ts : tres.getMap().get(Bytes.toBytes("data")).get(k).keySet()) {
					System.out.println("   Timestamp: " + ts);
				}
			}
		}

	}

	public static void main(String[] arg) {
		try {
			new ReadCompleteTsdb();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

}
