package de.tum.in.sonar.collector.server;

import org.apache.thrift.server.TNonblockingServer;
import org.apache.thrift.server.TServer;
import org.apache.thrift.transport.TNonblockingServerSocket;
import org.apache.thrift.transport.TNonblockingServerTransport;
import org.apache.thrift.transport.TTransportException;

import de.tum.in.sonar.collector.TsdService;

public class DataSinkServer {

	public DataSinkServer() {

	}

	void start() {
		try {
			TNonblockingServerTransport serverTransport = new TNonblockingServerSocket(
					7911);

			TsdServiceImpl impl = new TsdServiceImpl();
			TsdService.Processor processor = new TsdService.Processor(impl);

			TNonblockingServer.Args args = new TNonblockingServer.Args(
					serverTransport);
			args.processor(processor);

			TServer server = new TNonblockingServer(args);
			server.serve();

		} catch (TTransportException e) {
			e.printStackTrace();
		}
	}
}
