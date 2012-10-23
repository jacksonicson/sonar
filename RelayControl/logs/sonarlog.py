import logging
from collector import CollectService, ttypes
from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport
import time
import configuration as config

LOG_LEVELS = {60: 50010, 
              50:50000, 
              40:40000, 
              30:30000, 
              20:20000, 
              10:10000} 
SYNC = 60

logging.addLevelName(SYNC, 'SYNC')

loggingClient = None

logger = None

def connect():
    # Make socket
    global transportLogging
    transportLogging = TSocket.TSocket(config.COLLECTOR_IP, config.LOGGING_PORT)
    
    # Buffering is critical. Raw sockets are very slow
    transportLogging = TTransport.TBufferedTransport(transportLogging) 
    
    # Setup the clients
    global loggingClient
    loggingClient = CollectService.Client(TBinaryProtocol.TBinaryProtocol(transportLogging));
    
    # Open the transports
    transportLogging.open()

def close():
    transportLogging.close()

class SonarLogHandler(logging.Handler):
    def __init__(self, server, port, hostname, sensor, programName):
        logging.Handler.__init__(self)
        
        self.server = server
        self.port = port
        self.hostname = hostname
        self.sensor = sensor
        self.programName = programName
        
    def emit(self, record):
        ids = ttypes.Identifier()
        ids.timestamp = int(time.time())
        ids.sensor = self.sensor
        ids.hostname = self.hostname
        
        value = ttypes.LogMessage()
        value.logLevel = LOG_LEVELS[record.levelno]
        value.logMessage = record.getMessage()
        value.programName = self.programName
        value.timestamp = ids.timestamp
        
        loggingClient.logMessage(ids, value)

def getLogger(sensor, hostname=config.HOSTNAME):
    if loggingClient is None:
        connect()
          
    global logger
    if logger is None:
        logger = logging.getLogger("RelayControl")
        
        if config.SONAR_LOGGING:
            logger.addHandler(SonarLogHandler(config.COLLECTOR_IP, config.LOGGING_PORT, hostname, sensor, "RelayControl"))
        else:
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            logger.addHandler(ch)
        
        logger.setLevel(logging.DEBUG)
    
    return logger