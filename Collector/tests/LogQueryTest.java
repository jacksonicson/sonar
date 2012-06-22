import java.util.List;

import org.apache.thrift.TException;
import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.protocol.TProtocol;
import org.apache.thrift.transport.TSocket;
import org.apache.thrift.transport.TTransport;
import org.apache.thrift.transport.TTransportException;

import de.tum.in.sonar.collector.LogMessage;
import de.tum.in.sonar.collector.LogsQuery;
import de.tum.in.sonar.collector.ManagementService;

public class LogQueryTest {

	public static void main(String[] args) {

		TTransport transport;
		try {
			transport = new TSocket("localhost", 7931);
			transport.open();

			TProtocol protocol = new TBinaryProtocol(transport);

			ManagementService.Client client = new ManagementService.Client(
					protocol);

			LogsQuery query = new LogsQuery();

			query.setHostname("jack");
			query.setSensor("TEST");
			query.setStartTime(1340139600L);
			query.setStopTime(1340097755L);

			List<LogMessage> logMessages = client.queryLogs(query);
			System.out.println("Size :" + logMessages.size());

			for (LogMessage p : logMessages) {
				System.out.println(p);
			}

			transport.close();

		} catch (TTransportException e) {
			e.printStackTrace();
		} catch (TException e) {
			e.printStackTrace();
		}

	}

}
