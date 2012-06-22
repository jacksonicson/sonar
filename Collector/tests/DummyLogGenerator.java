import org.apache.thrift.TException;
import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.protocol.TProtocol;
import org.apache.thrift.transport.TSocket;
import org.apache.thrift.transport.TTransport;
import org.apache.thrift.transport.TTransportException;

import de.tum.in.sonar.collector.CollectService;
import de.tum.in.sonar.collector.Identifier;
import de.tum.in.sonar.collector.LogMessage;

public class DummyLogGenerator {

	public static void main(String[] args) {
		TTransport transport;
		try {
			transport = new TSocket("localhost", 7921);
			transport.open();

			TProtocol protocol = new TBinaryProtocol(transport);

			CollectService.Client client = new CollectService.Client(protocol);

			for (int i = 0; i < 10; i++) {

				Identifier id = new Identifier();
				id.setTimestamp(System.currentTimeMillis() / 1000 + i );
				id.setSensor("TEST");
				id.setHostname("jack");

				LogMessage message = new LogMessage();
				message.setLogLevel(5);
				message.setLogMessage("Test Log Message " + i);
				message.setProgramName("DummyLoadGenerator");
				client.logMessage(id, message);
			}

			transport.close();

		} catch (TTransportException e) {
			e.printStackTrace();
		} catch (TException e) {
			e.printStackTrace();
		}
	}

}
