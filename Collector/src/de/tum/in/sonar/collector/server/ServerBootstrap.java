package de.tum.in.sonar.collector.server;

import org.apache.thrift.server.TNonblockingServer;
import org.apache.thrift.server.TServer;
import org.apache.thrift.server.TSimpleServer;
import org.apache.thrift.transport.TNonblockingServerSocket;
import org.apache.thrift.transport.TNonblockingServerTransport;
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

				// Server (connects stransport and processor)
				TServer server = new TSimpleServer(new TSimpleServer.Args(serverTransport).processor(processor));

				server.serve();

			} catch (TTransportException e) {
				e.printStackTrace();
			}
		}
	}

	class ManagementServiceThread extends Thread {
		public void run() {
			try {
				TNonblockingServerTransport serverTransport = new TNonblockingServerSocket(7912);

				ManagementServiceImpl impl = new ManagementServiceImpl();
				ManagementService.Processor processor = new ManagementService.Processor(impl);

				TNonblockingServer.Args args = new TNonblockingServer.Args(serverTransport);
				args.processor(processor);

				TServer server = new TNonblockingServer(args);
//				server.serve();

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
			} catch (InterruptedException e) {
				logger.debug("server thread crashed", e);
			}
		}
	}
}
