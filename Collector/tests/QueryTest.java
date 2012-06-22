import java.util.List;

import org.apache.thrift.TException;
import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.protocol.TProtocol;
import org.apache.thrift.transport.TSocket;
import org.apache.thrift.transport.TTransport;
import org.apache.thrift.transport.TTransportException;

import de.tum.in.sonar.collector.ManagementService;
import de.tum.in.sonar.collector.TimeSeriesQuery;
import de.tum.in.sonar.collector.TransferableTimeSeriesPoint;

public class QueryTest {

	public static void main(String arg[]) {

		TTransport transport;
		try {
			transport = new TSocket("localhost", 7931);
			transport.open();

			TProtocol protocol = new TBinaryProtocol(transport);
			ManagementService.Client client = new ManagementService.Client(protocol);

			
			TimeSeriesQuery query = new TimeSeriesQuery();
			query.setHostname("jack");
			query.setSensor("CPU");
			query.setStartTime(1340096400L);
			query.setStopTime(Long.MAX_VALUE);

			List<TransferableTimeSeriesPoint> tsPoints = client.query(query);
			System.out.println("LENGTH " + tsPoints.size()); 
			for (TransferableTimeSeriesPoint p : tsPoints) {
				System.out.println("row: " + p.getTimestamp() + " : " + p.getValue());
			}

			transport.close();

		} catch (TTransportException e) {
			e.printStackTrace();
		} catch (TException e) {
			e.printStackTrace();
		}

	}
}
