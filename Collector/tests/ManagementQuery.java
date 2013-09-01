import java.io.IOException;
import java.util.Set;

import org.apache.thrift.TException;
import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.protocol.TProtocol;
import org.apache.thrift.transport.TSocket;
import org.apache.thrift.transport.TTransport;
import org.apache.thrift.transport.TTransportException;

import de.tum.in.sonar.collector.BundledSensorConfiguration;
import de.tum.in.sonar.collector.ManagementService;

public class ManagementQuery {

	public static void main(String arg[]) throws IOException {

		TTransport transport;
		try {
			transport = new TSocket("monitor0.dfg", 7931);
			transport.open();
			TProtocol protocol = new TBinaryProtocol(transport);
			ManagementService.Client client = new ManagementService.Client(protocol);

			Set<String> sensors = client.getSensors("monitor11");
			for (String sensor : sensors) {
				System.out.println(sensor);
			}

			BundledSensorConfiguration bundle = client.getBundledSensorConfiguration("psutilcpu", "srv0");
			System.out.println(bundle.active);

			transport.close();

		} catch (TTransportException e) {
			e.printStackTrace();
		} catch (TException e) {
			e.printStackTrace();
		}

	}
}
