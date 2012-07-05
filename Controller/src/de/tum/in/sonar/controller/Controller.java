package de.tum.in.sonar.controller;

import java.util.HashSet;
import java.util.Set;

import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.protocol.TProtocol;
import org.apache.thrift.server.TServer;
import org.apache.thrift.server.TSimpleServer;
import org.apache.thrift.transport.TServerSocket;
import org.apache.thrift.transport.TServerTransport;
import org.apache.thrift.transport.TSocket;
import org.apache.thrift.transport.TTransport;
import org.apache.thrift.transport.TTransportException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import de.tum.in.sonar.collector.NotificationClient;
import de.tum.in.sonar.collector.NotificationService;
import de.tum.in.sonar.collector.SensorToWatch;

public class Controller {

	private static Logger logger = LoggerFactory.getLogger(Controller.class);

	class ReceiverThread extends Thread {

		private Receiver receiver;

		public ReceiverThread(Receiver receiver) {
			this.receiver = receiver;
		}

		public void run() {
			try {
				// Service Processor
				NotificationClient.Processor processor = new NotificationClient.Processor(this.receiver);

				// Transport
				TServerTransport serverTransport = new TServerSocket(8000);

				// Server (connects transport and processor)
				TServer server = new TSimpleServer(new TSimpleServer.Args(serverTransport).processor(processor));

				logger.info("Starting ReceiverService ...");
				server.serve();
				logger.info("done");

			} catch (TTransportException e) {
				e.printStackTrace();
			}
		}
	}

	public Controller() {

		logger.info("Starting Controller...");

		// Start receiver
		Receiver receiver = new Receiver();
		ReceiverThread thread = new ReceiverThread(receiver);
		thread.start();

		// Subscribe events
		try {
			TTransport transport = new TSocket("localhost", 7911);
			transport.open();

			TProtocol protocol = new TBinaryProtocol(transport);

			NotificationService.Client client = new NotificationService.Client(protocol);

			String ip = "localhost";
			int port = 8000;

			Set<SensorToWatch> watchlist = new HashSet<SensorToWatch>();
			SensorToWatch watch = new SensorToWatch();
			watch.setHostname("localhost.localdomain");
			watch.setSensor("procpu");
			watchlist.add(watch);

			client.subscribe("localhost", 8000, watchlist);

			logger.info("Subscription finished");

			// Wait for thread to join
			thread.join();

		} catch (Exception e) {
			e.printStackTrace();
		}

	}

	public static void main(String arg[]) {
		new Controller();
	}

}
