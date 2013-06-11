package de.tum.in.sonar.collector.notification;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import de.tum.in.sonar.collector.tsdb.MetricPoint;

public class NotificationManager extends Thread {

	private static final Logger logger = LoggerFactory.getLogger(NotificationManager.class);

	private BlockingQueue<Notification> queue = new LinkedBlockingQueue<Notification>();
	private boolean running = true;

	private List<Connection> connections = new ArrayList<Connection>();

	public void notify(String hostname, String sensor, MetricPoint point) throws InterruptedException {
		Notification notification = new Notification(hostname, sensor, point);
		queue.put(notification);
	}

	public void addSubscription(Subscription subscription) {
		// Check if there is already a subscript for the IP address in the new subscription
		synchronized (connections) {
			for (Connection connection : connections) {
				logger.info("checking: " + connection.subscription.getIp() + " vs. " + subscription.getIp());

				if (connection.subscription.getIp().equals(subscription.getIp())) {
					logger.info("Extending watchlist of existing subscription");
					connection.subscription.extendWatchlist(subscription.getWatchlist());
					return;
				}
			}

			// Nothing found, so create a new connection for this subscription
			Connection connection = new Connection(subscription);
			connections.add(connection);
		}
	}

	private void deliver(List<Notification> notification) {
		synchronized (connections) {
			ArrayList<Connection> deleteList = new ArrayList<Connection>();

			for (Iterator<Connection> it = connections.iterator(); it.hasNext();) {
				Connection connection = it.next();
				try {
					connection.sendNotifications(notification);
				} catch (DeadSubscriptionException e) {
					logger.info("removing dead connection " + connection.subscription.dump());
					deleteList.add(connection);
				}
			}

			// Remove all dead connections
			for (Connection toDel : deleteList) {
				boolean status = connections.remove(toDel);
				logger.info("removing dead connection: " + status);
			}

			// Log number of remaining connections
			if (deleteList.size() > 0) {
				logger.info("remaining connections: " + connections.size());
			}
		}
	}

	public void run() {
		List<Notification> buffer = new ArrayList<Notification>(20);
		while (running) {
			try {
				Notification notification = queue.take();
				buffer.add(notification);
				if (buffer.size() > 10) {
					deliver(buffer);
					buffer.clear();
				}
			} catch (InterruptedException e) {
				logger.error("Error while processing notifications", e);
			}
		}
	}
}
