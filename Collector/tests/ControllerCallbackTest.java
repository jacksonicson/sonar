import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;

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
			List<Notification> toSend = new ArrayList<Notification>(1);
			toSend.add(not);
			conection.sendNotifications(toSend);
		} catch (DeadSubscriptionException e) {
			e.printStackTrace();
		}

		conection.close();

	}

	public static void main(String arg[]) {
		new ControllerCallbackTest();
	}
}
