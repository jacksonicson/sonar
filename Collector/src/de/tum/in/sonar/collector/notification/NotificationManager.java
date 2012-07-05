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
		Connection connection = new Connection(subscription);
		connections.add(connection);
	}

	private void deliver(Notification notification) {
		for (Iterator<Connection> it = this.connections.iterator(); it.hasNext();) {
			Connection connection = it.next();
			try {
				connection.send(notification);
			} catch (DeadSubscriptionException e) {
				logger.info("removing dead connection");
				it.remove();
			}
		}
	}

	public void run() {
		while (running) {
			try {
				Notification notification = queue.take();
				deliver(notification);
			} catch (InterruptedException e) {
				logger.error("Error while processing notifications", e);
			}
		}
	}
}
