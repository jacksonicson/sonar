import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class TestLogAppender {

	private static Logger logger = LoggerFactory.getLogger(TestLogAppender.class);

	public static void main(String[] args) {
		logger.error("Testing error log");
//		logger.info("Testing info log");
//		logger.warn("Testing warn log");
//		logger.debug("Testing debug log");
	}

}
