package de.tum.in.sonar.collector.server;

import org.apache.thrift.server.TNonblockingServer;
import org.apache.thrift.server.TServer;
import org.apache.thrift.server.TSimpleServer;
import org.apache.thrift.transport.TNonblockingServerSocket;
import org.apache.thrift.transport.TServerSocket;
import org.apache.thrift.transport.TServerTransport;
import org.apache.thrift.transport.TTransportException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import de.tum.in.sonar.collector.CollectService;
import de.tum.in.sonar.collector.ManagementService;
import de.tum.in.sonar.collector.NotificationService;

public class ServerBootstrap {

	private static final Logger logger = LoggerFactory.getLogger(ServerBootstrap.class);

	private CollectServiceImpl collectServiceImpl;
	private ManagementServiceImpl managementServiceImpl;
	private NotificationServiceImpl notificationServiceImpl;

	class NotificationServiceThread extends Thread {
		public void run() {
			try {
				// Service Processor
				NotificationService.Processor processor = new NotificationService.Processor(notificationServiceImpl);

				// Transport
				TServerTransport serverTransport = new TServerSocket(7911);

				// Server (connects transport and processor)
				TServer server = new TSimpleServer(new TSimpleServer.Args(serverTransport).processor(processor));

				logger.info("Starting NotificationService ...");
				server.serve();

			} catch (TTransportException e) {
				e.printStackTrace();
			}
		}
	}

	class CollectServiceThread extends Thread {
		public void run() {
			try {
				// Service Processor
				CollectService.Processor processor = new CollectService.Processor(collectServiceImpl);

				// Transport
				TServerTransport serverTransport = new TServerSocket(7921);

				// Server (connects transport and processor)
				TServer server = new TSimpleServer(new TSimpleServer.Args(serverTransport).processor(processor));

				logger.info("Starting CollectionService ...");
				server.serve();

			} catch (TTransportException e) {
				e.printStackTrace();
			}
		}
	}

	class CollectNonblockingServiceThread extends Thread {
		public void run() {
			try {
				// Service Processor
				CollectService.Processor processor = new CollectService.Processor(collectServiceImpl);

				// Transport
				TNonblockingServerSocket serverTransport = new TNonblockingServerSocket(7922);

				// Server (connects transport and processor)
				TServer server = new TNonblockingServer(
						new TNonblockingServer.Args(serverTransport).processor(processor));

				logger.info("Starting nonblocking CollectionService ...");
				server.serve();

			} catch (TTransportException e) {
				e.printStackTrace();
			}
		}
	}

	class ManagementServiceThread extends Thread {
		public void run() {
			try {
				// Service Processor
				ManagementService.Processor processor = new ManagementService.Processor(managementServiceImpl);

				// Nonblocking transport
				TServerSocket serverTransport = new TServerSocket(7931);

				TServer server = new TSimpleServer(new TSimpleServer.Args(serverTransport).processor(processor));

				logger.info("Starting blocking ManagementService ...");
				server.serve();

			} catch (TTransportException e) {
				e.printStackTrace();
			}
		}
	}

	class ManagementNonblockingServiceThread extends Thread {
		public void run() {
			try {
				// Service Processor
				ManagementService.Processor processor = new ManagementService.Processor(managementServiceImpl);

				// Nonblocking transport
				TNonblockingServerSocket serverTransport = new TNonblockingServerSocket(7932);

				TServer server = new TNonblockingServer(
						new TNonblockingServer.Args(serverTransport).processor(processor));

				logger.info("Starting nonblocking ManagementService ...");
				server.serve();

			} catch (TTransportException e) {
				e.printStackTrace();
			}
		}
	}

	public Thread[] start() {
		Thread[] threads = new Thread[] { new ManagementServiceThread(), new CollectServiceThread(),
				new ManagementNonblockingServiceThread(), new CollectNonblockingServiceThread(),
				new NotificationServiceThread() };

		for (Thread thread : threads) {
			thread.start();
		}

		return threads;
	}

	public void wait(Thread[] threads) {
		for (Thread thread : threads) {
			try {
				thread.join();
				logger.warn("Service thread joinged");
			} catch (InterruptedException e) {
				logger.error("server thread crashed", e);
			}
		}
	}

	public void setCollectServiceImpl(CollectServiceImpl collectServiceImpl) {
		this.collectServiceImpl = collectServiceImpl;
	}

	public void setManagementServiceImpl(ManagementServiceImpl managementServiceImpl) {
		this.managementServiceImpl = managementServiceImpl;
	}

}
