package de.tum.in.sonar.collector.notification;

import java.util.ArrayList;
import java.util.List;

import org.apache.thrift.TException;
import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.protocol.TProtocol;
import org.apache.thrift.transport.TSocket;
import org.apache.thrift.transport.TTransport;
import org.apache.thrift.transport.TTransportException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import de.tum.in.sonar.collector.Collector;
import de.tum.in.sonar.collector.NotificationClient;
import de.tum.in.sonar.collector.NotificationData;

public class Connection {

	private static Logger logger = LoggerFactory.getLogger(Collector.class);

	private final Subscription subscription;
	private TTransport transport;
	private NotificationClient.Client client;

	private int connectionRetries = 0;

	public Connection(Subscription subscription) {
		this.subscription = subscription;
		logger.info("New subscription: " + subscription.getIp() + ":" + subscription.getPort());
	}

	public void close() {
		if (transport != null) {
			if (transport.isOpen())
				transport.close();
		}
	}

	private boolean establish() {
		if (transport != null && transport.isOpen())
			return true;

		transport = new TSocket(subscription.getIp(), subscription.getPort());

		try {
			transport.open();
		} catch (TTransportException e) {
			logger.info("Error while creating callback transport object", e);
			return false;
		}

		TProtocol protocol = new TBinaryProtocol(transport);
		client = new NotificationClient.Client(protocol);

		return true;
	}

	private void checkConnection() throws DeadSubscriptionException {
		if (transport != null) {
			transport.close();

			logger.info("Reestablishing connection with receiver");

			connectionRetries++;
			if (connectionRetries > 3) {
				throw new DeadSubscriptionException(subscription);
			}

			establish();
		}
	}

	private void send(List<NotificationData> data) throws DeadSubscriptionException {
		try {
			establish();
			logger.debug("Sending data through the callback channel");
			client.receive(data);
		} catch (TException e) {
			logger.debug("Could not send notification data", e);
			checkConnection();
		}
	}

	public void send(Notification notification) throws DeadSubscriptionException {
		logger.info("Sending...");
		if (this.subscription.check(notification)) {
			List<NotificationData> set = new ArrayList<NotificationData>(1);

			NotificationData data = new NotificationData();
			data.setId(notification.getReading().getIdentifier());
			data.setReading(notification.getReading().getMetricReading());

			set.add(data);
			send(set);
		}
	}
}
