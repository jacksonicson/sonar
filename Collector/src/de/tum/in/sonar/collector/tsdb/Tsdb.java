package de.tum.in.sonar.collector.tsdb;

import java.io.IOException;
import java.util.HashSet;
import java.util.Set;

import org.apache.hadoop.hbase.HColumnDescriptor;
import org.apache.hadoop.hbase.HTableDescriptor;
import org.apache.hadoop.hbase.MasterNotRunningException;
import org.apache.hadoop.hbase.ZooKeeperConnectionException;
import org.apache.hadoop.hbase.client.HBaseAdmin;
import org.apache.hadoop.hbase.util.Bytes;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import de.tum.in.sonar.collector.Collector;
import de.tum.in.sonar.collector.HBaseUtil;

public class Tsdb {

	private static Logger logger = LoggerFactory.getLogger(Collector.class);

	private HBaseUtil hbaseUtil;

	private class InternalTableDescriptor implements Comparable<InternalTableDescriptor> {
		private final String name;

		private final String[] families;

		public InternalTableDescriptor(String name, String[] families) {
			this.name = name;
			this.families = families;
		}

		String getName() {
			return name;
		}

		String[] getFamilies() {
			return families;
		}

		@Override
		public int compareTo(InternalTableDescriptor o) {
			return name.compareTo(o.getName());
		}

		@Override
		public int hashCode() {
			return name.hashCode();
		}

		@Override
		public boolean equals(Object obj) {
			InternalTableDescriptor desc = (InternalTableDescriptor) obj;
			return name.equals(desc.getName());
		}
	}

	public void setupTables() {

		try {
			HBaseAdmin hbase = new HBaseAdmin(hbaseUtil.getConfig());

			// Table layout

			Set<InternalTableDescriptor> tables = new HashSet<InternalTableDescriptor>();
			tables.add(new InternalTableDescriptor("tsdb", new String[] { "data" }));
			tables.add(new InternalTableDescriptor("tsdb-uid", new String[] { "forward", "backward" }));
			tables.add(new InternalTableDescriptor("tsdb-label", new String[] { "tsdb-key" }));

			// Remove all existing table from the set
			HTableDescriptor tableDescriptors[] = hbase.listTables();
			for (HTableDescriptor desc : tableDescriptors) {
				String name = Bytes.toString(desc.getName());
				tables.remove(new InternalTableDescriptor(name, new String[] {}));

				logger.debug("Hbase table found: " + name);
			}

			// Create all remaining tables
			for (InternalTableDescriptor internalDesc : tables) {

				logger.debug("Hbase table create: " + internalDesc.getName());

				HTableDescriptor desc = new HTableDescriptor(internalDesc.getName());
				for (String family : internalDesc.getFamilies()) {
					HColumnDescriptor meta = new HColumnDescriptor(family.getBytes());
					desc.addFamily(meta);
				}

				hbase.createTable(desc);
			}

		} catch (MasterNotRunningException e) {
			e.printStackTrace();
		} catch (ZooKeeperConnectionException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}

	}

	public void writeData() 
	{
		
	}
	
	public void setHbaseUtil(HBaseUtil hbaseUtil) {
		this.hbaseUtil = hbaseUtil;
	}

}
