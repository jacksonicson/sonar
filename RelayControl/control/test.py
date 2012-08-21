import logging
import logging.handlers
import logs.sonarLogger as sonarLogger
                
# Set up a specific logger with our desired output level
my_logger = logging.getLogger('MyLogger')
my_logger.setLevel(logging.DEBUG)

# Add the log message handler to the logger
my_logger.addHandler(sonarLogger.SonarLogHandler("localhost", 7932, "jack", "test"))

# Log some messages
for i in range(20):
    my_logger.debug('i = %d' % i)