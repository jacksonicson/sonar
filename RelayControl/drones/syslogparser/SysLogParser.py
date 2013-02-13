import sys
import time
import datetime
import CollectService, ttypes
from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport

##########################
## Configuration        ##
COLLECTOR_IP = 'monitor0'
LOGGING_PORT = 7921
##########################

LOG_LEVELS = {60: 50010, 
              50:50000, 
              40:40000, 
              30:30000, 
              20:20000, 
              10:10000} 

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
    
def parseSyslog(logLines):
    #split lines
    words = logLines.split(" ")
    
    #get timestamp
    s = words[0] + "/" + words[1] + "/2012 " + words[2]
    timestamp = time.mktime(datetime.datetime.strptime(s, "%b/%d/%Y %H:%M:%S").timetuple())
    
    #get hostname
    hostname = words[3];
    
    #get program name
    programName = words[4].split('[')[0];
    
    #get the log message
    logMessage = "";
    for x in range(5, len(words)):
        logMessage += words[x] +" "
    
    #create identifier
    ids = ttypes.Identifier()
    ids.timestamp = int(timestamp)
    ids.sensor = "SysLogParserDrone"
    ids.hostname = hostname
    
    #create the log message 
    value = ttypes.LogMessage()
    value.logLevel = LOG_LEVELS[10]
    value.logMessage = logMessage
    value.programName = programName
    value.timestamp = ids.timestamp
    
    #log the message to the sonar server
    loggingClient.logMessage(ids, value)

#get the file name to be parsed from sys args
FILE_NAME = sys.argv[1]
try:
    #connect to sonar server
    connect()
    
    #open the file and parse every line
    f = open(FILE_NAME)
    for line in iter(f):
        parseSyslog(line)
    f.close()
    
    #close connection to sonar server
    close()
except IOError as e:
    print "I/O error({0}): {1}".format(e.errno, e.strerror)

    