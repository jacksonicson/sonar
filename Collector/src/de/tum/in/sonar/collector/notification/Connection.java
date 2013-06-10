package de.tum.in.sonar.collector.notification;

import java.util.ArrayList;
import java.util.List;

import org.apache.thrift.TException;
import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.protocol.TProtocol;
import org.apache.thrift.transport.TSocket;
import org.apache.thrift.transport.TTransport;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import de.tum.in.sonar.collector.Collector;
import de.tum.in.sonar.collector.NotificationClient;
import de.tum.in.sonar.collector.NotificationData;

public class Connection {

	private static Logger logger = LoggerFactory.getLogger(Collector.class);

	final Subscription subscription;
	private TTransport transport;
	private NotificationClient.Client client;

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

	private boolean establish() throws DeadSubscriptionException {
		try {
			if (transport != null && transport.isOpen())
				return true;
		} catch (Exception e) {
			// do nothing
		}

		try {
			transport = new TSocket(subscription.getIp(), subscription.getPort(), 6000);
			transport.open();
			TProtocol protocol = new TBinaryProtocol(transport);
			client = new NotificationClient.Client(protocol);
			return true;

		} catch (Exception e) {
			logger.info("Error while creating callback transport object", e);
			throw new DeadSubscriptionException(subscription);
		}
	}

	private void send(List<NotificationData> data) throws DeadSubscriptionException {
		if (establish()) {
			try {
				client.receive(data);
			} catch (TException e) {
				logger.warn("Could not send data");
				throw new DeadSubscriptionException(subscription);
			}
		}
	}

	public void send(Notification notification) throws DeadSubscriptionException {
		if (this.subscription.check(notification)) {
			List<NotificationData> set = new ArrayList<NotificationData>(1);

			NotificationData data = new NotificationData();
			data.setId(notification.getReading().getIdentifier());
			data.setReading(notification.getReading().getMetricReading());

			set.add(data);
			send(set);
		}
	}

	@Override
	public int hashCode() {
		return subscription.getIp().hashCode();
	}

	@Override
	public boolean equals(Object obj) {
		if (!(obj instanceof Connection))
			return false;

		Connection test = (Connection) obj;
		return (test.subscription.equals(subscription));
	}
}
