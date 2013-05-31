import java.io.ByteArrayOutputStream;
import java.io.FileInputStream;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.util.HashSet;
import java.util.Set;

import org.apache.thrift.TException;
import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.protocol.TProtocol;
import org.apache.thrift.transport.TSocket;
import org.apache.thrift.transport.TTransport;
import org.apache.thrift.transport.TTransportException;

import de.tum.in.sonar.collector.BundledSensorConfiguration;
import de.tum.in.sonar.collector.ManagementService;
import de.tum.in.sonar.collector.SensorConfiguration;
import de.tum.in.sonar.collector.SensorType;

public class ManagementTest {

	private static ByteBuffer file() throws IOException {
		ByteArrayOutputStream out = new ByteArrayOutputStream();
		FileInputStream in = new FileInputStream("D:/work/sonar/Collector/build/collector.jar");
		byte[] buffer = new byte[256];
		int len = 0;
		while ((len = in.read(buffer)) > 0) {
			out.write(buffer, 0, len);
		}
		return ByteBuffer.wrap(out.toByteArray());
	}

	public static void main(String arg[]) throws IOException {

		TTransport transport;
		try {
			transport = new TSocket("localhost", 7931);
			transport.open();
			TProtocol protocol = new TBinaryProtocol(transport);
			ManagementService.Client client = new ManagementService.Client(protocol);

			long id = System.currentTimeMillis();
			String host = "Host" + id;
			String sensor = "Sensor" + id;

			client.addHost(host);
			client.addHostExtension(host, "DUMMY");
			client.getHostExtension(host);
			client.getAllHosts();

			SensorConfiguration configuration = new SensorConfiguration();
			client.setSensorConfiguration(sensor, configuration);

			configuration.setSensorExtends("test");
			configuration.setSensorType(SensorType.LOG);
			configuration.setInterval(100);
			client.updateSensorConfiguration(sensor, configuration, new HashSet<String>());

			client.deploySensor(sensor, file());
			client.fetchSensor(sensor);

			configuration = client.getSensorConfiguration(sensor);
			assert (configuration.getSensorExtends().equals("test"));
			assert (configuration.getSensorType() == SensorType.LOG);
			assert (configuration.getInterval() == 100);

			String md5 = client.sensorHash(sensor);
			assert (md5.length() > 5);

			boolean binary = client.hasBinary(sensor);
			assert (binary);

			Set<String> names = client.getSensorNames();
			assert (names.size() > 1);

			Set<String> sensors = client.getAllSensors();
			assert (sensors.size() > 1);

			client.setSensor(host, sensor, true);
			Set<String> assigned = client.getSensors(host);
			assert (assigned.contains(sensor));
			assert (assigned.size() == 1);

			BundledSensorConfiguration bconfig = client.getBundledSensorConfiguration(sensor, host);
			assert (bconfig.isActive());

			client.setSensor(host, sensor, false);
			assigned = client.getSensors(host);
			assert (assigned.size() == 0);
			assert (!assigned.contains(sensor));

			bconfig = client.getBundledSensorConfiguration(sensor, host);
			assert (!bconfig.isActive());

			// client.delHost(host);
			// client.delSensor(sensor);

			// Set<String> hosts = client.getAllHosts();
			// for(String host : hosts) {
			// client.getLabels(host);
			// Set<String> sensors = client.getSensors(host);
			// for(String sensor : sensors) {
			// client.getBundledSensorConfiguration(sensor, host);
			// }
			// }
			// client.getAllSensors();
			//
			// // Sensors
			// System.out.println("sensors");
			// Set<String> sensors = client.getSensors("target150");
			// System.out.println("done " + sensors.size());
			// for (String sensor : sensors) {
			// System.out.println("Sensor: " + sensor);
			// }

			// client.getAllSensors();

			// String data = "Really new sensor version";
			// byte[] ds = Bytes.toBytes(data);
			// client.deploySensor("cpu", ByteBuffer.wrap(ds));
			//
			// client.addHost("test");
			// Set<String> labels = new HashSet<String>();
			// labels.add("asdf");
			// client.setHostLabels("test", labels);
			//
			// System.out.println("Labels: " + client.getLabels("test"));
			//
			//

			//
			// SensorConfiguration configuration = new SensorConfiguration();
			// configuration.setInterval(1);
			// client.setSensorConfiguration("cpu", configuration);
			//
			// Set<String> labels = client.getLabels("srv2");
			// for (String label : labels) {
			// System.out.println("Label: " + label);
			// }
			//
			// ByteArrayOutputStream out = new ByteArrayOutputStream();
			// InputStream in = new FileInputStream("cpu.zip");
			//
			// byte[] buffer = new byte[32];
			// int len = 0;
			// while ((len = in.read(buffer)) > 0) {
			// out.write(buffer, 0, len);
			// }
			//
			// System.out.println("Uploading sensor package now ...");
			// client.deploySensor("cpu", ByteBuffer.wrap(out.toByteArray()));
			// System.out.println("OK");

			//
			//
			// String data = "Really new sensor version";
			// byte[] ds = Bytes.toBytes(data);
			// client.deploySensor("cpu", ByteBuffer.wrap(ds));
			//
			// ds = client.fetchSensor("cpu").array();
			// System.out.println("Datea: " + Bytes.toString(ds));
			//
			// client.addHost("srv2");
			//
			// client.delHost("srv2");
			//
			// client.addHost("srv2");
			//
			// Set<String> labels = new HashSet<String>();
			// labels.add("test");
			// labels.add("hello");
			// client.setHostLabels("srv2", labels);
			//
			//
			//
			// client.setSensor("srv2", "cpu", true);
			//
			// client.setSensorLabels("cpu", labels);
			//
			// client.setSensorConfiguration("cpu", ByteBuffer.wrap(ds));

			transport.close();

		} catch (TTransportException e) {
			e.printStackTrace();
		} catch (TException e) {
			e.printStackTrace();
		}

	}
}
