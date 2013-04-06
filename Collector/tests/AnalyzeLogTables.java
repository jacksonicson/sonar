import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.NavigableMap;

import org.apache.hadoop.hbase.client.HTable;
import org.apache.hadoop.hbase.client.Result;
import org.apache.hadoop.hbase.client.ResultScanner;
import org.apache.hadoop.hbase.client.Scan;
import org.apache.hadoop.hbase.util.Bytes;
import org.apache.thrift.TDeserializer;
import org.apache.thrift.TException;

import de.tum.in.sonar.collector.HBaseUtil;
import de.tum.in.sonar.collector.LogMessage;
import de.tum.in.sonar.collector.log.LogConstants;

public class AnalyzeLogTables {

	public AnalyzeLogTables() throws IOException {

		HBaseUtil util = new HBaseUtil();

		HTable table = new HTable(util.getConfig(), LogConstants.TABLE_LOG);

		Scan scan = new Scan();
		scan.setBatch(500);
		ResultScanner scanner = table.getScanner(scan);

		long crt = 0;
		long length = 0;
		long counter = 0;
		long n = 0;
		double mean = 0;
		double M2 = 0;

		BufferedWriter out = new BufferedWriter(new FileWriter("C:/temp/msgs.txt"));

		for (Result res : scanner) {
			byte[] key = res.getRow();

			long sensorId = Bytes.toLong(key, 0);
			long hostnameId = Bytes.toLong(key, 8);
			long timestamp = Bytes.toLong(key, 16);

			// System.out.println(sensorId + "|" + hostnameId + "|" + timestamp);

			NavigableMap<byte[], byte[]> families = res.getFamilyMap(Bytes.toBytes("data"));
			TDeserializer deserializer = new TDeserializer();
			for (byte[] fkey : families.keySet()) {
				byte[] value = families.get(fkey);
				LogMessage logMsg = new LogMessage();
				try {
					deserializer.deserialize(logMsg, value);
				} catch (TException e) {
					continue;
				}

				// Update mean
				// mean = (mean * (double)counter + logMsg.getLogMessage().length()) / (double)(counter + 1);
				// counter++;

				n++;
				double x = logMsg.getLogMessage().length();
				double delta = x - mean;
				mean = mean + delta / (double) n;
				M2 = M2 + delta * (x - mean);

				out.write(Long.toString(logMsg.getTimestamp()));
				out.write(",");
				out.write(Integer.toString(logMsg.getLogMessage().length()));
				out.newLine();
			}

			if (crt++ % 500 == 0) {
				try {
					Thread.sleep(1000);
					System.out.println("Counter: " + crt);
					double variance_n = M2 / (double) n;
					double variance = M2 / (double) (n - 1);
					System.out.println("stdev: " + Math.sqrt(variance));
					System.out.println("mean: " + mean);

				} catch (InterruptedException e) {
					e.printStackTrace();
				}
			}
		}

		table.close();
		out.close();

		double avg = (double) length / (double) crt;
		System.out.println("Average length: " + avg);
		System.out.println("Counter: " + crt);

	}

	public static void main(String[] arg) {
		try {
			new AnalyzeLogTables();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

}
