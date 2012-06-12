import java.util.HashSet;
import java.util.Random;
import java.util.Set;

import org.apache.thrift.TException;
import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.protocol.TProtocol;
import org.apache.thrift.transport.TSocket;
import org.apache.thrift.transport.TTransport;
import org.apache.thrift.transport.TTransportException;

import de.tum.in.sonar.collector.CollectService;
import de.tum.in.sonar.collector.Identifier;
import de.tum.in.sonar.collector.MetricReading;

public class DummyLoadGenerator {

	public static void main(String arg[]) {

		TTransport transport;
		try {
			transport = new TSocket("localhost", 7921);
			transport.open();

			TProtocol protocol = new TBinaryProtocol(transport);

			CollectService.Client client = new CollectService.Client(protocol);

			Random rand = new Random();
			long time = System.currentTimeMillis();
			System.out.println("current timestamp: " + time);
			for (int i = 0; i < 5; i++) {

				Identifier id = new Identifier();
				id.setTimestamp(time / 1000);
				id.setHostname("jack");
				id.setSensor("CPU");

				MetricReading tsp = new MetricReading();
				Set<String> labels = new HashSet<String>();
				tsp.setLabels(labels);

				tsp.setValue(Math.abs(rand.nextInt()));

				client.logMetric(id, tsp);
			}

			transport.close();

		} catch (TTransportException e) {
			e.printStackTrace();
		} catch (TException e) {
			e.printStackTrace();
		}

	}
}
