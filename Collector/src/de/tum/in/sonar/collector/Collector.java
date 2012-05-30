package de.tum.in.sonar.collector;

import java.io.IOException;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import de.tum.in.sonar.collector.server.CollectServiceImpl;
import de.tum.in.sonar.collector.server.ManagementServiceImpl;
import de.tum.in.sonar.collector.server.ServerBootstrap;
import de.tum.in.sonar.collector.tsdb.TableCreationException;
import de.tum.in.sonar.collector.tsdb.TimeSeriesDatabase;

public class Collector {

	private static Logger logger = LoggerFactory.getLogger(Collector.class);

	public Collector() throws IOException {

		HBaseUtil hbase = new HBaseUtil();

		TimeSeriesDatabase tsdb = new TimeSeriesDatabase();
		tsdb.setHbaseUtil(hbase);
		try {
			tsdb.setupTables();
		} catch (TableCreationException e) {
			logger.error("Error while creating HBase talbe structure", e);
			System.exit(1);
		}

		CollectServiceImpl collectService = new CollectServiceImpl();
		collectService.setTsdb(tsdb);

		ManagementServiceImpl managementService = new ManagementServiceImpl();

		ServerBootstrap dataSinkServer = new ServerBootstrap();
		dataSinkServer.setCollectServiceImpl(collectService);
		dataSinkServer.setManagementServiceImpl(managementService);

		logger.info("Starting severs...");
		Thread[] threads = dataSinkServer.start();
		logger.info("Sever started");

		dataSinkServer.wait(threads);
	}

	public static void main(String[] args) {

		try {
			new Collector();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
}
