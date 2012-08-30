from collector import CollectService, ManagementService, ttypes
from datetime import datetime
from select import select
from subprocess import Popen, PIPE
from threading import Thread
from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport
import json
import numpy as np
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
    schedule_metrics = {}
    rain_metric = {}
    sonar_metrics = {}
     
    for host in hosts:
        query = ttypes.LogsQuery()
        query.hostname = host
        query.sensor = 'rain'
        query.startTime = frame[0]
        query.stopTime = frame[1]
        
        logs = sonar.queryLogs(query)
        
        STR_BENCHMARK_SCHEDULE = 'Schedule: '
        for log in logs:
            if log.logMessage.startswith(STR_BENCHMARK_SCHEDULE):
                msg = log.logMessage[len(STR_BENCHMARK_SCHEDULE):]
                data = json.loads(msg)
                schedule_metrics[host] = data
                frame = (frame[0], int(data['endRun'] / 1000))
                break
        
        
        STR_RAIN_METRICS = 'Rain metrics: '
        STR_DEALER_METRICS = 'Dealer metrics: '
        STR_MFG_METRICS = 'Mfg metrics: ' 
        
        # scan logs for results
        for log in logs:
            if log.timestamp > (frame[1] + 5 * 60) * 1000:
                print 'skipping log message, out of time frame'
                break
            
            if log.logMessage.startswith(STR_RAIN_METRICS):
                msg = log.logMessage[len(STR_RAIN_METRICS):]
                data = json.loads(msg)
                
                if rain_metric.has_key(host) == False:
                    rain_metric[host] = []
                    
                rain_metric[host].append(data)
                
            if log.logMessage.startswith(STR_DEALER_METRICS):
                msg = log.logMessage[len(STR_DEALER_METRICS):]
                data = json.loads(msg)
                
                if sonar_metrics.has_key(host) == False:
                    sonar_metrics[host] = []
                    
                sonar_metrics[host].append(data)
                
            if log.logMessage.startswith(STR_MFG_METRICS):
                msg = log.logMessage[len(STR_MFG_METRICS):]
                data = json.loads(msg)
                
                if sonar_metrics.has_key(host) == False:
                    sonar_metrics[host] = []
                    
                sonar_metrics[host].append(data) 
                
            
    return schedule_metrics, rain_metric, sonar_metrics


def __to_array(sonar_ts):
    data = np.empty(len(sonar_ts), dtype=float)
    
    index = 0
    for element in sonar_ts:
        data[index] = element.value 
        index += 1
    
    return data

def __fetch_srv_data(sonar, hosts, sensor, frame):
    results = []
    for host in hosts:
        query = ttypes.TimeSeriesQuery()
        query.hostname = host
        query.startTime = frame[0]
        query.stopTime = frame[1]
        query.sensor = sensor
        
        result = sonar.query(query)
        result = __to_array(result)
        results.append(result)
        
    return results

def __to_timestamp(date):
    res = time.strptime(date, '%d.%m.%Y %H:%M')    
    return int(time.mktime(res))


def main():
    # Connect with services
    sonar_client = __connect()
    
    try:
        # Configure experiment
        start = __to_timestamp('30.08.2012 15:40')
        stop = __to_timestamp('31.08.2012 8:00')
        frame = (start, stop)
        
        controller = 'Andreas-PC'
        load = ['load0', ]
        syncs = __fetch_start_benchamrk_syncs(sonar_client, controller, frame)
        if syncs == None:
            print 'error: no start marker found'
            return
        frame = (syncs, frame[1])
        
        rain_schedule, rain_metrics, sonar_metrics = __fetch_rain_data(sonar_client, load, frame)
        
        # Update frame
        startRun = int(rain_schedule[load[0]]['startSteadyState'] / 1000)
        endRun = int(rain_schedule[load[0]]['endSteadyState'] / 1000)
        frame = (startRun, endRun)
        duration = frame[1] - frame[0]
        print duration
              
        # Load srv data
        srvs = [ 'srv%i' % i for i in range(0, 6)]
        res_cpu = __fetch_srv_data(sonar_client, srvs, 'psutilcpu', frame)
        phy_mem = __fetch_srv_data(sonar_client, srvs, 'psutilmem.phymem', frame)
        vir_mem = __fetch_srv_data(sonar_client, srvs, 'psutilmem.virtmem', frame)
        
        # Analytics
        # Server ours for each server
        avg_cpu_load = []
        for i in xrange(len(srvs)):
            cpu = res_cpu[i]
            avg = np.average(cpu)
            avg_cpu_load.append(avg)
            print 'average load on %s: %f' % (srvs[i], avg) 
        
        # Prints
        for rain_metric in rain_metrics.keys():
            rain_metric_ist = rain_metrics[rain_metric]
            for rain_metric in rain_metric_ist:
                print 'track: %s' % (rain_metric['track'])
                print '   average_operation_response_time(s): %s' % (rain_metric['average_operation_response_time(s)'])
                print '   effective_load(req/sec): %s' % (rain_metric['effective_load(req/sec)'])
                print '   effective_load(ops/sec): %s' % (rain_metric['effective_load(ops/sec)'])
        
    except:
        traceback.print_exc(file=sys.stdout)
    
    __disconnect()

if __name__ == '__main__':
    main()
