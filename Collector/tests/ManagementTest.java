import java.nio.ByteBuffer;

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

			transport.close();

		} catch (TTransportException e) {
			e.printStackTrace();
		} catch (TException e) {
			e.printStackTrace();
		}

	}
}
