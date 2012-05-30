import java.util.HashSet;
import java.util.Set;

import org.apache.thrift.TException;
import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.protocol.TProtocol;
import org.apache.thrift.transport.TSocket;
import org.apache.thrift.transport.TTransport;
import org.apache.thrift.transport.TTransportException;

import de.tum.in.sonar.collector.CollectService;
import de.tum.in.sonar.collector.Identifier;
import de.tum.in.sonar.collector.TimeSeriesPoint;

public class DummyLoadGenerator {

	public static void main(String arg[]) {

		TTransport transport;
		try {
			transport = new TSocket("localhost", 7911);
			transport.open();

			TProtocol protocol = new TBinaryProtocol(transport);

			CollectService.Client client = new CollectService.Client(protocol);

			Identifier id = new Identifier();
			id.setTimestamp(System.currentTimeMillis());
			id.setSensor(1234);
			id.setHostname("jack");

			client.logMessage(id, "hello world");

			Set<String> labels = new HashSet<String>();
			labels.add("cpu");
			labels.add("test");
			labels.add("experiment1");

			TimeSeriesPoint tsp = new TimeSeriesPoint();
			tsp.setLabels(labels);
			tsp.setValue(33);

			client.logMetric(id, tsp);

			transport.close();

		} catch (TTransportException e) {
			e.printStackTrace();
		} catch (TException e) {
			e.printStackTrace();
		}

	}
}
