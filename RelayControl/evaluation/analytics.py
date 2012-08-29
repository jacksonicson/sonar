from collector import CollectService, ManagementService, ttypes
from datetime import datetime
from select import select
from subprocess import Popen, PIPE
from threading import Thread
from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport
import json
import sys
import time
import traceback

##########################
## Configuration        ##
COLLECTOR_IP = 'monitor0'
MANAGEMENT_PORT = 7931
LOGGING_PORT = 7921
DEBUG = False
##########################

def __disconnect():
    transportManagement.close()

def __connect():
    # Make socket
    global transportManagement
    transportManagement = TSocket.TSocket(COLLECTOR_IP, MANAGEMENT_PORT)
    
    # Buffering is critical. Raw sockets are very slow
    transportManagement = TTransport.TBufferedTransport(transportManagement)
    
    # Setup the clients
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


def __fetch_start_benchamrk_syncs(sonar, host, frame):
    query = ttypes.LogsQuery()
    query.hostname = host
    query.sensor = 'start_benchmark'
    query.startTime = frame[0]
    query.stopTime = frame[1]
    
    logs = sonar.queryLogs(query)
    for log in logs:
        if log.logLevel == 50010:
            if log.logMessage == 'start driving load':
                print log
                return log.timestamp
            
    return None

def __fetch_rain_data(sonar, hosts, frame):
    result = []
    for host in hosts:
        query = ttypes.LogsQuery()
        query.hostname = host
        query.sensor = 'rain'
        query.startTime = frame[0]
        query.stopTime = frame[1]
        
        logs = sonar.queryLogs(query)
        print 'logs loaded...'
        
        rampup_finished = '[TRACK: track5] Ramp up finished!'
        rain_stopped = 'Rain stopped'
        
        for log in logs:
            if log.logMessage.startswith('[{"result":"DealerMetrics","description":"description"},'):
                data = json.loads(log.logMessage)
                print data
                
                result.append(data)
                
                break
             
    return result
        


def __fetch_controller_data(connection, host, frame):
    pass


def __fetch_srv_data(sonar, hosts, sensor, frame):
    for host in hosts:
        query = ttypes.TimeSeriesQuery()
        query.hostname = host
        query.startTime = frame[0]
        query.stopTime = frame[1]
        query.sensor = sensor
        
        result = sonar.query(query)
        return result
        


def __to_timestamp(date):
    res = time.strptime(date, '%d.%m.%Y %H:%M')    
    return int(time.mktime(res))


def main():
    # Connect with services
    sonar_client = __connect()
    
    try:
        # Configure experiment
        start = __to_timestamp('24.08.2012 17:10')
        stop = __to_timestamp('28.08.2012 8:00')
        frame = (start, stop)
        
        syncs = __fetch_start_benchamrk_syncs(sonar_client, 'Andreas-PC', frame)
        if syncs == None:
            print 'No start marker found'
            return
        
        frame = (syncs, frame[1])
        rain = __fetch_rain_data(sonar_client, ('load0', 'load1'), frame)
        if rain == None:
            print 'No Rain stats found'
            
        for set in rain:
            for element in set:
                if element['description'] == 'Purchase: Vehicle Purchasing Rate (/sec)':
                    print element['result']

        
        # No controller active
        # Load controller data
        # control = __fetch_controller_data(sonar_client, ('Andreas-PC'), frame)
        
        # Load srv* data
        srvs = [ 'srv%i' % i for i in range(0, 6)]
        res_cpu = __fetch_srv_data(sonar_client, srvs, 'psutilcpu', frame)
        print len(res_cpu)
        
        
    except:
        traceback.print_exc(file=sys.stdout)
     
    



    
    __disconnect()

if __name__ == '__main__':
    main()
