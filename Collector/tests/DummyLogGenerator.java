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
			transport = new TSocket("monitor0.dfg", 7921);
			transport.open();

			TProtocol protocol = new TBinaryProtocol(transport);

			CollectService.Client client = new CollectService.Client(protocol);

			long time = System.currentTimeMillis() / 1000; 
			for (int i = 0; i < 20; i++) {

				Identifier id = new Identifier();
				// Use the same timestmpa
				id.setTimestamp(time);
				id.setSensor("TEST");
				id.setHostname("Andreas-PC");

				LogMessage message = new LogMessage();
				message.setLogLevel(5);
				message.setLogMessage("Test Log Message 2 " + i);
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
