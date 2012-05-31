import java.nio.ByteBuffer;
import java.util.HashSet;
import java.util.Set;

import org.apache.hadoop.hbase.util.Bytes;
import org.apache.thrift.TException;
import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.protocol.TProtocol;
import org.apache.thrift.transport.TSocket;
import org.apache.thrift.transport.TTransport;
import org.apache.thrift.transport.TTransportException;

import de.tum.in.sonar.collector.ManagementService;

public class ManagementTest {

	public static void main(String arg[]) {

		TTransport transport;
		try {
			transport = new TSocket("localhost", 7912);
			transport.open();

			TProtocol protocol = new TBinaryProtocol(transport);

			ManagementService.Client client = new ManagementService.Client(protocol);

			String data = "Really new sensor version";
			byte[] ds = Bytes.toBytes(data);
			client.deploySensor("cpu", ByteBuffer.wrap(ds));

			ds = client.fetchSensor("cpu").array();
			System.out.println("Datea: " + Bytes.toString(ds));

			client.addHost("srv2");

			client.delHost("srv2");

			client.addHost("srv2");

			Set<String> labels = new HashSet<String>();
			labels.add("test");
			labels.add("hello");
			client.setHostLabels("srv2", labels);

			labels = client.getLabels("srv2");
			for (String label : labels) {
				System.out.println("Label: " + label);
			}

			client.setSensor("srv2", "cpu", true);

			client.setSensorLabels("cpu", labels);

			client.setSensorConfiguration("cpu", ByteBuffer.wrap(ds));

			transport.close();

		} catch (TTransportException e) {
			e.printStackTrace();
		} catch (TException e) {
			e.printStackTrace();
		}

	}
}
