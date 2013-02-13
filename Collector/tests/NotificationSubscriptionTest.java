import java.util.HashSet;
import java.util.Set;

import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.protocol.TProtocol;
import org.apache.thrift.transport.TSocket;
import org.apache.thrift.transport.TTransport;

import de.tum.in.sonar.collector.NotificationService;
import de.tum.in.sonar.collector.SensorToWatch;

public class NotificationSubscriptionTest {

	public NotificationSubscriptionTest() throws Exception {
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
		System.out.println("subscribed");

		client.unsubscribe("localhost");
		System.out.println("unsubscribed");

	}

	public static void main(String arg[]) {
		try {
			new NotificationSubscriptionTest();
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

}
