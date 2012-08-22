import logging
from collector import CollectService, ttypes
from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport
import time

logLevels = {60: 50010, 50:50000, 40:40000, 30:30000, 20:20000, 10:10000} 

# Set up a specific logger with our desired output level
SYNC = 60
logging.addLevelName(SYNC, 'SYNC')

# Log handler
class SonarLogHandler(logging.Handler): # Inherit from logging.Handler
    def __init__(self, server, port, hostname, sensor, programName):
            # run the regular Handler __init__
            logging.Handler.__init__(self)
            # Our custom argument
            self.server = server
            self.port = port
            self.hostname = hostname
            self.sensor = sensor
            self.programName = programName
            
            transportLogging = TSocket.TSocket(self.server, self.port)
            transportLogging = TTransport.TBufferedTransport(transportLogging) 
            transportLogging.open();
            self.loggingClient = CollectService.Client(TBinaryProtocol.TBinaryProtocol(transportLogging))
              
            
    def emit(self, record):
            # record.message is the log message
            ids = ttypes.Identifier()
            ids.timestamp = int(time.time())
            ids.sensor = self.sensor
            ids.hostname = self.hostname
            
            value = ttypes.LogMessage()
            value.logLevel = logLevels[record.levelno]
            value.logMessage = record.getMessage()
            value.programName = self.programName
            value.timestamp = ids.timestamp
            self.loggingClient.logMessage(ids, value)
            