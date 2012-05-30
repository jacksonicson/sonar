import java.io.IOException;

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
		Get get = new Get();

		Scan scan = new Scan();

		System.out.println("Scanning over the rows:");
		ResultScanner scanner = table.getScanner(scan);
		for (Result res : scanner) {
			System.out.println("Row: " + res.getRow());

			byte[] key = res.getRow();

			int sensorId = Bytes.toInt(key, 0);
			System.out.println("Sensor: " + sensorId);

			long timestamp = Bytes.toLong(key, 4);
			System.out.println("Timestamp: " + timestamp);

			int hostnameId = Bytes.toInt(key, 12);
			System.out.println("Hostname: " + hostnameId);

			// All the tags
			System.out.println("Reading tags: ");
			int offset = 16;
			while (offset < key.length) {
				int tagId = Bytes.toInt(key, offset);
				System.out.println("Tag id: " + tagId);
				offset += 4;
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
