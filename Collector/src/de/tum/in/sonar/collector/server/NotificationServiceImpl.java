package de.tum.in.sonar.collector.server;

import java.util.Set;

import org.apache.commons.lang.NotImplementedException;
import org.apache.thrift.TException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import de.tum.in.sonar.collector.NotificationService;
import de.tum.in.sonar.collector.SensorToWatch;
import de.tum.in.sonar.collector.notification.NotificationManager;
import de.tum.in.sonar.collector.notification.Subscription;

public class NotificationServiceImpl implements NotificationService.Iface {

	private static final Logger logger = LoggerFactory.getLogger(NotificationServiceImpl.class);

	private NotificationManager notifyManager;

	@Override
	public void subscribe(String ip, int port, Set<SensorToWatch> watchlist) throws TException {
		logger.info("New subscription");

		Subscription subscription = new Subscription(ip, port, watchlist);
		notifyManager.addSubscription(subscription);
	}

	@Override
	public void unsubscribe(String ip) throws TException {
		logger.info("Unsubscribing");
		throw new NotImplementedException();
	}

	public void setNotificationManager(NotificationManager notifyManager) {
		this.notifyManager = notifyManager;
	}
}
