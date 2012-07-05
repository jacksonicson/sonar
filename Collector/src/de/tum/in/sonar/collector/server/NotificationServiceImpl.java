package de.tum.in.sonar.collector.server;

import java.util.Set;

import org.apache.thrift.TException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import de.tum.in.sonar.collector.NotificationService;
import de.tum.in.sonar.collector.SensorToWatch;

public class NotificationServiceImpl implements NotificationService.Iface {

	private static final Logger logger = LoggerFactory.getLogger(NotificationServiceImpl.class);

	@Override
	public void subscribe(String ip, int port, Set<SensorToWatch> watchlist) throws TException {
		logger.info("New subscription");
	}

	@Override
	public void unsubscribe(String ip) throws TException {
		logger.info("Unsubscribing");
	}
}
