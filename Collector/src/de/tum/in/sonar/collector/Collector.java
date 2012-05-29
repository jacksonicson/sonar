package de.tum.in.sonar.collector;

import java.io.IOException;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.hbase.HBaseConfiguration;
import org.apache.hadoop.hbase.client.HTable;
import org.apache.hadoop.hbase.client.Put;
import org.apache.hadoop.hbase.client.Result;
import org.apache.hadoop.hbase.client.ResultScanner;
import org.apache.hadoop.hbase.client.Scan;
import org.apache.hadoop.hbase.util.Bytes;

public class Collector {

	public Collector() throws IOException {

		// Test some HBase stuff

		// Server: 192.168.110.108

		Configuration config = HBaseConfiguration.create();

		/*
		 * HBaseAdmin hbase = new HBaseAdmin(config); HTableDescriptor desc =
		 * new HTableDescriptor("TEST");
		 * 
		 * HColumnDescriptor meta = new
		 * HColumnDescriptor("personal".getBytes());
		 * 
		 * HColumnDescriptor prefix = new
		 * HColumnDescriptor("account".getBytes());
		 * 
		 * desc.addFamily(meta); desc.addFamily(prefix);
		 * 
		 * hbase.createTable(desc);
		 */

		System.out.println("New table statement");

		HTable testTable = new HTable(config, "TEST");

		System.out.println("New table statement done ");

		for (int i = 0; i < 100; i++) {
			byte[] family = Bytes.toBytes("personal");
			byte[] qual = Bytes.toBytes("account");

			Scan scan = new Scan();
			scan.addColumn(family, qual);

			ResultScanner rs = testTable.getScanner(scan);

			for (Result r = rs.next(); r != null; r = rs.next()) {
				byte[] valueObj = r.getValue(family, qual);
				int value = Bytes.toInt(valueObj); 
				System.out.println("value: " + value);
			}

//			Put put = new Put(Bytes.toBytes(i));
//			put.add(family, qual, Bytes.toBytes(i));
//			testTable.put(put);
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
