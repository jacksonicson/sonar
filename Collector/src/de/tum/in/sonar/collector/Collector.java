package de.tum.in.sonar.collector;

import java.io.IOException;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.hbase.HBaseConfiguration;
import org.apache.hadoop.hbase.client.HTable;
import org.apache.hadoop.hbase.client.Result;
import org.apache.hadoop.hbase.client.ResultScanner;
import org.apache.hadoop.hbase.client.Scan;
import org.apache.hadoop.hbase.util.Bytes;

public class Collector {

	public Collector() throws IOException {

		// Test some HBase stuff

		// Server: 192.168.110.108

		Configuration config = HBaseConfiguration.create();
		config.set("hbase.zookeeper.quorum", "hadoop1");

		HTable testTable = new HTable(config, "test");

		for (int i = 0; i < 100; i++) {
			byte[] family = Bytes.toBytes("cf");
			byte[] qual = Bytes.toBytes("a");

			Scan scan = new Scan();
			scan.addColumn(family, qual);
			ResultScanner rs = testTable.getScanner(scan);
			for (Result r = rs.next(); r != null; r = rs.next()) {
				byte[] valueObj = r.getValue(family, qual);
				String value = new String(valueObj);
				System.out.println(value);
			}
		}

		testTable.close();

	}

	public static void main(String[] args) {
		try {
			new Collector();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
}
