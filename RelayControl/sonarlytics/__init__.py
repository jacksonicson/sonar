'''
This is the base package used by all analysis scripts to connect
with Sonar monitoring and download data. 
'''

from collector import ManagementService, ttypes
from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport
import time
from workload import util

##########################
## Configuration        ##
##########################
COLLECTOR_IP = 'monitor0'
MANAGEMENT_PORT = 7931
LOGGING_PORT = 7921
##########################


'''
Disconnect from Sonar collector
'''
def __disconnect():
    transportManagement.close()


'''
Connect with Sonar collector 
'''
def __connect():
    # Make socket
    global transportManagement
    transportManagement = TSocket.TSocket(COLLECTOR_IP, MANAGEMENT_PORT)
    transportManagement = TTransport.TBufferedTransport(transportManagement)
    
    global managementClient
    managementClient = ManagementService.Client(TBinaryProtocol.TBinaryProtocol(transportManagement));
    
    # Open the transports
    while True:
        try:
            transportManagement.open();
            break
        except Exception:
            print 'Retrying connection...'
            time.sleep(1)
            
    return managementClient 

# Connect
__connect()

'''
Convert a datetime from a string to a UNIX timestamp
'''
def to_timestamp(date):
    res = time.strptime(date, '%d/%m/%Y %H:%M:%S')    
    return int(time.mktime(res))

'''
Fetch a timeseries
'''
def fetch_timeseries(host, sensor, timeframe):
    global managementClient
    
    query = ttypes.TimeSeriesQuery()
    query.hostname = host
    query.startTime = timeframe[0]
    query.stopTime = timeframe[1]
    query.sensor = sensor
    
    result = managementClient.query(query)
    time, result = util.to_array_collector(result, timeframe)
        
    return result, time


'''
Fechtes log data
'''
def fetch_logs(load_host, sensor, timeframe):
    global managementClient
    
    # Build query
    query = ttypes.LogsQuery()
    query.hostname = load_host
    query.sensor = 'rain'
    query.startTime = timeframe[0]
    query.stopTime = timeframe[1]
    logs = managementClient.queryLogs(query)
    
    return logs
