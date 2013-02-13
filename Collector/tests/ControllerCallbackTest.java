import java.util.HashSet;

import de.tum.in.sonar.collector.Identifier;
import de.tum.in.sonar.collector.MetricReading;
import de.tum.in.sonar.collector.NotificationData;
import de.tum.in.sonar.collector.SensorToWatch;
import de.tum.in.sonar.collector.notification.Connection;
import de.tum.in.sonar.collector.notification.DeadSubscriptionException;
import de.tum.in.sonar.collector.notification.Notification;
import de.tum.in.sonar.collector.notification.Subscription;
import de.tum.in.sonar.collector.tsdb.MetricPoint;

public class ControllerCallbackTest {

	public ControllerCallbackTest() {

		Subscription subscriptiont = new Subscription("localhost", 9876, new HashSet<SensorToWatch>());

		Connection conection = new Connection(subscriptiont);

		NotificationData data = new NotificationData();
		data.id = new Identifier();
		data.reading = new MetricReading();

		Notification not = new Notification("asdf", "asdf", new MetricPoint(data.id, data.reading));
		try {
			conection.send(not);
		} catch (DeadSubscriptionException e) {
			e.printStackTrace();
		}
		
		conection.close(); 

	}

	public static void main(String arg[]) {
		new ControllerCallbackTest();
	}
}
