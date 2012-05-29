package de.tum.in.sonar.collector;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.hbase.HBaseConfiguration;

public class HBaseUtil {

	private final Configuration config;

	public HBaseUtil() {
		this.config = HBaseConfiguration.create();
	}

	public Configuration getConfig() {
		return this.config;
	}

}
