import logging
import logs.sonarLogger as sonarLogger
                
# Set up a specific logger with our desired output level
SYNC = 60  # positive yet important
logging.addLevelName(SYNC, 'SYNC')      # new level
my_logger = logging.getLogger('MyLogger')
my_logger.setLevel(logging.DEBUG)

# Add the log message handler to the logger
my_logger.addHandler(sonarLogger.SonarLogHandler("localhost", 7921, "jack", "TEST", "progName"))

# Log some messages
for i in range(20):
    my_logger.debug('debug log %d' % i)
    my_logger.log(SYNC, 'sync statements')