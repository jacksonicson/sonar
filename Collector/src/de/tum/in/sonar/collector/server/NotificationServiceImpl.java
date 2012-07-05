package de.tum.in.sonar.collector.server;

import java.util.HashSet;
import java.util.Set;

import org.apache.thrift.TException;
import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.protocol.TProtocol;
import org.apache.thrift.transport.TSocket;
import org.apache.thrift.transport.TTransport;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import de.tum.in.sonar.collector.NotificationClient;
import de.tum.in.sonar.collector.NotificationData;
import de.tum.in.sonar.collector.NotificationService;
import de.tum.in.sonar.collector.SensorToWatch;

public class NotificationServiceImpl implements NotificationService.Iface {

	private static final Logger logger = LoggerFactory.getLogger(NotificationServiceImpl.class);

	@Override
	public void subscribe(String ip, int port, Set<SensorToWatch> watchlist) throws TException {
		logger.info("New subscription");

		TTransport transport = new TSocket(ip, port);
		transport.open();

		TProtocol protocol = new TBinaryProtocol(transport);

		NotificationClient.Client client = new NotificationClient.Client(protocol);

		Set<NotificationData> data = new HashSet<NotificationData>();
		client.receive(data);

		logger.info("callback done");

		transport.close();
		logger.info("transport closed");
	}

	@Override
	public void unsubscribe(String ip) throws TException {
		logger.info("Unsubscribing");
	}
}
