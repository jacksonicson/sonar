import logging
from collector import CollectService, ttypes
from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport
import time
from socket import gethostname

##########################
## Configuration        ##
COLLECTOR_IP = 'monitor0'
LOGGING_PORT = 7921
HOSTNAME = gethostname()
##########################

LOG_LEVELS = {60: 50010, 
              50:50000, 
              40:40000, 
              30:30000, 
              20:20000, 
              10:10000} 
SYNC = 60
INFO = 30
logging.addLevelName(SYNC, 'SYNC')

loggingClient = None

def connect():
    # Make socket
    global transportLogging
    transportLogging = TSocket.TSocket(COLLECTOR_IP, LOGGING_PORT)
    
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

def getLogger(sensor, hostname=HOSTNAME):
    if loggingClient is None:
        connect()
             
    logger = logging.getLogger("RelayControl")
    logger.addHandler(SonarLogHandler(COLLECTOR_IP, LOGGING_PORT, hostname, sensor, "RelayControl"))
    logger.setLevel(logging.DEBUG)
    
    return logger