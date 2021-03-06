package de.tum.in.sonar.collector.server;

import org.apache.thrift.TException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import de.tum.in.sonar.collector.CollectService;
import de.tum.in.sonar.collector.File;
import de.tum.in.sonar.collector.Identifier;
import de.tum.in.sonar.collector.LogMessage;
import de.tum.in.sonar.collector.MetricReading;
import de.tum.in.sonar.collector.log.LogDatabase;
import de.tum.in.sonar.collector.notification.NotificationManager;
import de.tum.in.sonar.collector.tsdb.MetricPoint;
import de.tum.in.sonar.collector.tsdb.TimeSeriesDatabase;

public class CollectServiceImpl implements CollectService.Iface {

	private static final Logger logger = LoggerFactory.getLogger(CollectServiceImpl.class);

	private NotificationManager notifyManager;
	private TimeSeriesDatabase tsdb;
	private LogDatabase logdb;

	@Override
	public void logMetric(Identifier id, MetricReading value) throws TException {

		// Create a new metric point
		MetricPoint dp = new MetricPoint(id, value);

		// Write it to the TSDB
		tsdb.writeData(dp);

		// Notify clients
		try {
			notifyManager.notify(id.getHostname(), id.getSensor(), dp);
		} catch (InterruptedException e) {
			logger.error("Error while notifing clients", e);
		}
	}

	@Override
	public void logMessage(Identifier id, LogMessage message) throws TException {
		// log message received
		logger.debug("log message");
		logdb.writeData(id, message);
	}

	@Override
	public void logResults(Identifier id, File file) throws TException {
		logger.warn("log results - not implemented");
	}

	public void setTsdb(TimeSeriesDatabase tsdb) {
		this.tsdb = tsdb;
	}

	public LogDatabase getLogdb() {
		return logdb;
	}

	public void setLogdb(LogDatabase logdb) {
		this.logdb = logdb;
	}

	public void setNotificationManager(NotificationManager notifyManager) {
		this.notifyManager = notifyManager;
	}

}
