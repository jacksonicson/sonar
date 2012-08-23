from collector import CollectService, ManagementService, ttypes
from socket import gethostname
from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport
import time

##########################
## Configuration        ##
COLLECTOR_IP = 'monitor0'
MANAGEMENT_PORT = 7931
LOGGING_PORT = 7921
HOSTNAME = gethostname()
##########################

loggingClient = None

def log(sensor, logValue):
    if loggingClient == None:
        connect()
    
    ids = ttypes.Identifier();
    ids.timestamp = int(time.time())
    ids.sensor = sensor
    ids.hostname = HOSTNAME
            
    value = ttypes.MetricReading();
    value.value = logValue
    value.labels = []
                
    # Send message
    loggingClient.logMetric(ids, value)

def connect(self):
    # Make socket
    transportLogging = TSocket.TSocket(COLLECTOR_IP, LOGGING_PORT)
    
    # Buffering is critical. Raw sockets are very slow
    transportLogging = TTransport.TBufferedTransport(transportLogging) 
    
    # Setup the clients
    global loggingClient
    loggingClient = CollectService.Client(TBinaryProtocol.TBinaryProtocol(transportLogging));
    
    # Open the transports
    transportLogging.open();
