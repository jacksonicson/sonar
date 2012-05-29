package de.tum.in.sonar.collector.server;

import org.apache.thrift.server.TNonblockingServer;
import org.apache.thrift.server.TServer;
import org.apache.thrift.transport.TNonblockingServerSocket;
import org.apache.thrift.transport.TNonblockingServerTransport;
import org.apache.thrift.transport.TTransportException;

import de.tum.in.sonar.collector.CollectService;

public class DataSinkServer {

	public void start() {
		try {
			TNonblockingServerTransport serverTransport = new TNonblockingServerSocket(7911);

			CollectServiceImpl impl = new CollectServiceImpl();
			CollectService.Processor processor = new CollectService.Processor(impl);

			TNonblockingServer.Args args = new TNonblockingServer.Args(serverTransport);
			args.processor(processor);

			TServer server = new TNonblockingServer(args);
			server.serve();

		} catch (TTransportException e) {
			e.printStackTrace();
		}
	}
}
