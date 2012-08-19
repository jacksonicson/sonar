import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class TestLogAppender {

	private static Logger logger = LoggerFactory.getLogger(TestLogAppender.class);

	public static void main(String[] args) {
		for (int i = 0; i < 100; i++) {
			logger.error("Testing error log");
			logger.info("Testing info log");
			logger.warn("Testing warn log");
			logger.debug("Testing debug log");
			if (i == 33) {
				try {
					String x = null;
					x.toString();
				} catch (Exception e) {
					logger.error("Error error", e);
				}
			}
		}

		System.out.println("DONE");

		org.apache.log4j.LogManager.shutdown();
	}

}
