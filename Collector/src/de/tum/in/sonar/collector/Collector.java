package de.tum.in.sonar.collector;

import java.io.IOException;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import de.tum.in.sonar.collector.server.DataSinkServer;
import de.tum.in.sonar.collector.tsdb.Tsdb;

public class Collector {

	private static Logger logger = LoggerFactory.getLogger(Collector.class);

	public Collector() throws IOException {

		HBaseUtil hbase = new HBaseUtil();

		Tsdb tsdb = new Tsdb();
		tsdb.setHbaseUtil(hbase);
		tsdb.setupTables();

		DataSinkServer dataSinkServer = new DataSinkServer();
		logger.info("Starting DataSink sever...");
		dataSinkServer.start();
	}

	public static void main(String[] args) {

		try {
			new Collector();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
}
