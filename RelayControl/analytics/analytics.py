from collector import CollectService, ManagementService, ttypes
from datetime import datetime
from select import select
from service import times_client
from subprocess import Popen, PIPE
from threading import Thread
from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport
from times import ttypes as times_ttypes
from workload import profiles
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

START = '04/09/2012 09:41:00'
END = '04/09/2012 16:07:00'
controller = 'Andreas-PC'
drivers = 'load0'
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
            if log.logMessage == 'start driving drivers':
                print 'found: start driving drivers'
                return log.timestamp
            
    return None

'''
Extracts all important data from a rain log
'''
def __fetch_rain_data(sonar, host, frame):
    schedule = None
    rain_config = None
    track_config = None
    track_metrics = []
    track_scorecards = []
    rain_metrics = []
    spec_metrics = { 'dealer':[], 'mfg':[]}
     
    query = ttypes.LogsQuery()
    query.hostname = host
    query.sensor = 'rain'
    query.startTime = frame[0]
    query.stopTime = frame[1]
    
    logs = sonar.queryLogs(query)
    
    # Refine timings
    STR_BENCHMARK_SCHEDULE = 'Schedule: '
    for log in logs:
        if log.logMessage.startswith(STR_BENCHMARK_SCHEDULE):
            msg = log.logMessage[len(STR_BENCHMARK_SCHEDULE):]
            schedule = json.loads(msg)
            schedule = (schedule['startSteadyState'], schedule['endSteadyState'])
            break
    
    
    # scan logs for results
    for log in logs:
        if log.timestamp > (frame[1] + 5 * 60) * 1000:
            print 'skipping remaining log messages - out of time frame'
            break
        
        # Track configuration
        STR_TRACK_CONFIG = 'Track configuration: '
        if log.logMessage.startswith(STR_TRACK_CONFIG):
            msg = log.logMessage[len(STR_TRACK_CONFIG):]
            data = json.loads(msg)
            track_config = data
            
        # Read rain metrics
        STR_RAIN_METRICS = 'Rain metrics: '
        if log.logMessage.startswith(STR_RAIN_METRICS):
            msg = log.logMessage[len(STR_RAIN_METRICS):]
            data = json.loads(msg)
            rain_metrics.append(data)
            
        # Read specj metrics
        STR_DEALER_METRICS = 'Dealer metrics: '
        if log.logMessage.startswith(STR_DEALER_METRICS):
            msg = log.logMessage[len(STR_DEALER_METRICS):]
            data = json.loads(msg)
            spec_metrics['dealer'].append(data)
            
        # Read MFG metrics
        STR_MFG_METRICS = 'Mfg metrics: '
        if log.logMessage.startswith(STR_MFG_METRICS):
            msg = log.logMessage[len(STR_MFG_METRICS):]
            data = json.loads(msg)
            spec_metrics['mfg'].append(data) 
              
        # Read track metrics
        STR_TRACK_METRICS = 'Track metrics: '
        if log.logMessage.startswith(STR_TRACK_METRICS):
            msg = log.logMessage[len(STR_TRACK_METRICS):]
            data = json.loads(msg)
            track_metrics.append(data)
        
        # Read track scorecard
        STR_TRACK_SCORECARD = 'Track scorecard: '
        if log.logMessage.startswith(STR_TRACK_SCORECARD):
            msg = log.logMessage[len(STR_TRACK_SCORECARD):]
            data = json.loads(msg)
            track_scorecards.append(data)
          
            
    return schedule, rain_config, track_config, rain_metrics, spec_metrics, track_metrics


def __to_array(sonar_ts):
    data = np.empty(len(sonar_ts), dtype=float)
    time = np.empty(len(sonar_ts), dtype=float)
    
    index = 0
    for element in sonar_ts:
        data[index] = element.value
        time[index] = element.timestamp 
        index += 1
    
    return data, time

def __fetch_srv_data(sonar, host, sensor, frame):
    query = ttypes.TimeSeriesQuery()
    query.hostname = host
    query.startTime = frame[0]
    query.stopTime = frame[1]
    query.sensor = sensor
    
    result = sonar.query(query)
    result, time = __to_array(result)
        
    return result, time

def __to_timestamp(date):
    res = time.strptime(date, '%d/%m/%Y %H:%M:%S')    
    return int(time.mktime(res))


def __dump_elements(elements):
    result = ['%s,' for _ in xrange(len(elements))]
    result = ' '.join(result)
    result = result[0:-1] # remove trailing comma
    print result % elements

def main():
    # Connect with services
    sonar_client = __connect()
    
    try:
        # Configure experiment
        start = __to_timestamp(START)
        stop = __to_timestamp(END)
        frame = (start, stop)
        
        # Get sync markers from control 
        sync_markers = __fetch_start_benchamrk_syncs(sonar_client, controller, frame)
        
        ### Reporting #######################################################################
        
        # Fetch rain data
        schedule, rain_config, track_config, rain_metrics, spec_metrics, track_metrics = __fetch_rain_data(sonar_client, drivers, frame)
        
        print '## SCHEDULE ##'
        print schedule
        steady_start, steady_end = schedule
        elements = (steady_start, steady_end)
        __dump_elements(elements)
        
        print '## DOMAIN WORKLOAD MAPS ##'
        domains = []
        domain_track_map = {}
        domain_workload_map = {}
        for track in track_config:
            host = track_config[track]['target']['hostname']
            workload = track_config[track]['loadScheduleCreatorParameters']['profile']
            
            if host not in domains:
                domains.append(host)
            
            if domain_track_map.has_key(host) == False:
                domain_track_map[host] = []
                
            domain_track_map[host].append(track)

            if domain_workload_map.has_key(host) == False:
                domain_workload_map[host] = workload
            else:
                if domain_workload_map[host] != workload:
                    print 'WARN: Multiple load profiles on the same target'
                    
        print 'domain track map: %s' % domain_track_map
        print 'domain workload map: %s' % domain_workload_map
                                                       
        print '## TRACK METRICS ##'
        for metric in track_metrics: 
            track = metric['track']
            effective_load = metric['effective_load(req/sec)']
            offered_load = metric['offered_load(ops/sec)']
             
            elements = (track, effective_load, offered_load)
            __dump_elements(elements)
            
                        
        print '## HOST - TRACK MAP ##'
        print domain_track_map
        print domain_workload_map
        
        print '## RAIN METRICS SUMMARY ##'
        total_op_initiated = 0
        total_op_successful = 0
        total_offered_load = 0
        total_ops_sec = 0
        total_req_sec = 0
        total_resp_time = 0
        total_max_resp_time = 0
        total_min_resp_time = 999
        for metric in rain_metrics:
            track = metric['track']
            if track.find('DealerGenerator') > 0: track = 'Dealer'
            else: track = 'MFG'
            
            op_initiated = metric['operations_initiated']
            op_successful = metric['operations_successfully_completed']
            offered_load = float(metric['offered_load(ops/sec)'])
            ops_sec = float(metric['effective_load(ops/sec)'])
            req_sec = float(metric['effective_load(req/sec)'])
            resp_time = float(metric['average_operation_response_time(s)'])
            
            total_op_initiated += op_initiated
            total_op_successful += op_successful
            total_offered_load += offered_load
            total_ops_sec += ops_sec
            total_req_sec += req_sec
            total_resp_time = (total_resp_time + resp_time) / 2.0
            
            min_resp_time = 999
            max_resp_time = 0
            for operation in metric['operational']['operations']:
                min_resp_time = min(min_resp_time, operation['min_response'])
                max_resp_time = max(max_resp_time, operation['max_response'])
                
            total_max_resp_time = max(max_resp_time, total_max_resp_time)
            total_min_resp_time = min(total_min_resp_time, min_resp_time)
            
            elements = (track, op_initiated, op_successful, offered_load, ops_sec, req_sec, resp_time, max_resp_time, min_resp_time)
            __dump_elements(elements)
            
        print '## TOTAL ##'
        elements = (total_op_initiated, total_op_successful, total_offered_load, total_ops_sec, total_req_sec, total_resp_time, total_max_resp_time, total_min_resp_time)
        __dump_elements(elements)
        # process spec_metrics
        # not required at this point
        
        # process CPU load of servers
        srvs = [ 'srv%i' % i for i in range(0, 6)]
        cpu = {}
        mem = {}
        print '## CPU LOAD SERVERS ##'
        for srv in srvs:
            res_cpu, tim_cpu = __fetch_srv_data(sonar_client, srv, 'psutilcpu', frame)
            res_mem, tim_mem = __fetch_srv_data(sonar_client, srv, 'psutilmem.phymem', frame)
            cpu[srv] = res_cpu
            mem[srv] = res_mem
#            print '%s cpu= %s' % (srv, res_cpu)
#            print '%s mem= %s' % (srv, res_mem)
        
        print '## CPU LOAD DOMAINS ##'
        for domain in domains:
            res_cpu, tim_cpu = __fetch_srv_data(sonar_client, domain, 'psutilcpu', frame)
            res_mem, tim_mem = __fetch_srv_data(sonar_client, domain, 'psutilmem.phymem', frame)
            cpu[domain] = (res_cpu, tim_cpu)
            mem[domain] = (res_mem, tim_mem)
#            print '%s cpu= %s' % (domain, res_cpu)
#            print '%s mem= %s' % (domain, res_mem)
        
        ### Generate and write CPU profiles to Times ########################################
        for domain in domain_workload_map.keys():
            print '###'
            print domain
            print domain_workload_map[domain]
            
            # Create profile from cpu load
            name = domain_workload_map[domain]
            profiles.process(name, cpu[domain][0], cpu[domain][1], True)
            
        
        ### Analytics #######################################################################
        print '## AVG CPU,MEM LOAD ##'
        for srv in srvs: 
            load = cpu[srv]
            _cpu = np.average(load)
            load = mem[srv]
            _mem = np.average(load)
            print '%s cpu: %f mem: %f' % (srv, _cpu, _mem)
        
        
        
    except:
        traceback.print_exc(file=sys.stdout)
    
    __disconnect()

if __name__ == '__main__':
    main()
