package de.tum.in.sonar.collector.notification;

import java.util.HashSet;
import java.util.Set;

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
		establish();
	}

	void close() {
		if (transport != null) {
			if (transport.isOpen())
				transport.close();
		}
	}

	private boolean establish() {
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

	private void send(Set<NotificationData> data) throws DeadSubscriptionException {
		try {
			logger.debug("Sending data through the callback channel");
			client.receive(data);
		} catch (TException e) {
			logger.debug("Could not send notification data", e);
			checkConnection();
		}
	}

	void send(Notification notification) throws DeadSubscriptionException {
		if (this.subscription.check(notification)) {
			Set<NotificationData> set = new HashSet<NotificationData>();

			NotificationData data = new NotificationData();
			data.setId(notification.getReading().getIdentifier());
			data.setReading(notification.getReading().getMetricReading());

			set.add(data);
			send(set);
		}
	}
}
