package de.tum.in.sonar.collector.server;

import org.apache.thrift.server.TServer;
import org.apache.thrift.server.TSimpleServer;
import org.apache.thrift.transport.TServerSocket;
import org.apache.thrift.transport.TServerTransport;
import org.apache.thrift.transport.TTransportException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import de.tum.in.sonar.collector.CollectService;
import de.tum.in.sonar.collector.ManagementService;

public class ServerBootstrap {

	private static final Logger logger = LoggerFactory.getLogger(ServerBootstrap.class);

	class CollectServiceThread extends Thread {
		public void run() {
			try {

				// Service Implementationt
				CollectServiceImpl impl = new CollectServiceImpl();

				// Service Processor
				CollectService.Processor processor = new CollectService.Processor(impl);

				// Transport
				TServerTransport serverTransport = new TServerSocket(7911);

				// Server (connects transport and processor)
				TServer server = new TSimpleServer(new TSimpleServer.Args(serverTransport).processor(processor));

				logger.info("Starting CollectionService ...");
				server.serve();

			} catch (TTransportException e) {
				e.printStackTrace();
			}
		}
	}

	class ManagementServiceThread extends Thread {
		public void run() {
			try {
				// Service implementation
				ManagementServiceImpl impl = new ManagementServiceImpl();

				// Service Processor
				ManagementService.Processor processor = new ManagementService.Processor(impl);

				// Nonblocking transport
				TServerTransport serverTransport = new TServerSocket(7912);

				// Parameters for the server
				TSimpleServer.Args args = new TSimpleServer.Args(serverTransport);
				args.processor(processor);

				// Server
				TServer server = new TSimpleServer(args);

				logger.info("Starting ManagementService ...");
				server.serve();

			} catch (TTransportException e) {
				e.printStackTrace();
			}
		}
	}

	public Thread[] start() {
		Thread[] threads = new Thread[] { new ManagementServiceThread(), new CollectServiceThread() };

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
}
