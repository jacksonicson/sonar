from collector import CollectService, ManagementService, ttypes
from datetime import datetime
from service import times_client
from subprocess import Popen, PIPE
from threading import Thread
from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport
from times import ttypes as times_ttypes
from virtual import nodes
from workload import profiles, util
import json
import numpy as np
import sys
import time
import traceback

##########################
## Configuration        ##
##########################
COLLECTOR_IP = 'monitor0'
MANAGEMENT_PORT = 7931
LOGGING_PORT = 7921
DEBUG = False
TRACE_EXTRACT = False

CONTROLLER_NODE = 'Andreas-PC'
DRIVER_NODES = ['load0', 'load1']

# RAW = '08/10/2012 09:35:46    08/10/2012 16:20:46'
RAW = '04/11/2012 12:45:00    04/11/2012 16:30:00'
##########################

warns = []

# If RAW exists use this one
START = ''
END = ''
if RAW is not None:
    START, END = RAW.split('    ')

'''
Log warning
'''
def __warn(msg):
    warns.append(msg)
    
'''
Dump warnings
'''
def __dump_warns():
    if len(warns) > 0:
        print '## WARNINGS ##'
        print 'Analysis might be invalid due to following warnings:'
        for warn in warns:
            print ' * %s' % warn

'''
Dump the configuration
'''
def __dump_configuration():
    print '## CONFIGURATION ##'
    print "COLLECTOR_IP = '%s'" % (COLLECTOR_IP)
    print 'MANAGEMENT_PORT = %i' % (MANAGEMENT_PORT)
    print 'LOGGING_PORT = %i' % (LOGGING_PORT)
    print 'DEBUG = %s' % (DEBUG)
    print 'TRACE_EXTRACT = %s' % (TRACE_EXTRACT)
    print ''
    print "CONTROLLER_NODE = '%s'" % (CONTROLLER_NODE)
    print "DRIVER_NODES = %s" % DRIVER_NODES
    print ''
    print "START = '%s'" % START
    print "END = '%s'" % END


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


'''
Read allocation configuration
'''
def __fetch_allocation_config(sonar, host, frame):
    query = ttypes.LogsQuery()
    query.hostname = host
    query.sensor = 'allocate_domains'
    query.startTime = frame[0] - 60 * 60 # Scan 10 minutes before the start_benchmark
    query.stopTime = frame[0] + 1 * 60 # Cannot occur after the benchmark start. Due to testing there may 
    # also be invalid entries after benchmark start. So, pick the first one before the benchmark.  
        
    servers = 0
    assignment = None
    migrations = None
    placement = None
    matrix = None
    
    logs = sonar.queryLogs(query)
    for log in logs:
        print log
        # Track configuration
        CONFIG = 'Required servers: '
        if log.logMessage.startswith(CONFIG):
            msg = log.logMessage[len(CONFIG):]
            servers = int(msg)
            
        CONFIG = 'Assignment: '
        if log.logMessage.startswith(CONFIG):
            msg = log.logMessage[len(CONFIG):]
            assignment = msg
            
        CONFIG = 'Migrations: '
        if log.logMessage.startswith(CONFIG):
            msg = log.logMessage[len(CONFIG):]
            migrations = msg
            
        CONFIG = 'Placement strategy: '
        if log.logMessage.startswith(CONFIG):
            msg = log.logMessage[len(CONFIG):]
            placement = msg
        
        CONFIG = 'Service matrix: '
        if log.logMessage.startswith(CONFIG):
            msg = log.logMessage[len(CONFIG):]
            matrix = msg
        
        CONFIG = 'Initial Active Servers: '
        if log.logMessage.startswith(CONFIG):
            msg = log.logMessage[len(CONFIG):]
            msg = json.loads(msg)
            servers = msg['count']
            
    return servers, assignment, migrations, placement, matrix
    

'''
Reads the sync markers from the start_benchmark skript: 
- start driving load  (releasing load)
- end of startup sequence (after ramp-up)
'''
def __fetch_start_benchamrk_syncs(sonar, host, frame):
    query = ttypes.LogsQuery()
    query.hostname = host
    query.sensor = 'start_benchmark'
    query.startTime = frame[0]
    query.stopTime = frame[1]
    logs = sonar.queryLogs(query)
    
    start_startup = None
    release_load = None
    end_startup = None
    for log in logs:
        if log.logLevel == 50010:
            if log.logMessage == 'start driving load':
                release_load = log.timestamp
            elif log.logMessage == 'end of startup sequence':
                end_startup = log.timestamp
            elif log.logMessage == 'start of startup sequence':
                start_startup = log.timestamp
                
                
    return start_startup, release_load, end_startup


'''
Extracts all migrations and their parameters
'''
def __fetch_migrations(connection, load_host, timeframe):
    # Build query
    query = ttypes.LogsQuery()
    query.hostname = load_host
    query.sensor = 'controller'
    query.startTime = timeframe[0]
    query.stopTime = timeframe[1]
    logs = connection.queryLogs(query)
    
    # Sync marker load balancer release
    sync_release = None
    
    # List of migrations
    successful = []
    failed = []
    server_active = [] 
    
    # scan logs for results
    for log in logs:
        if log.timestamp > timeframe[1]:
            print 'skipping remaining migrations - out of timeframe'
            break
        
        if sync_release:        
            if log.logLevel == 50010:
                if log.logMessage == 'Releasing load balancer':
                    sync_release = log.timestamp
        else:
            # Migration triggered
            STR_MIGRATION_TRIGGERED = 'Live Migration Triggered: '
            if log.logMessage.startswith(STR_MIGRATION_TRIGGERED):
                log.logMessage[len(STR_MIGRATION_TRIGGERED):]
            
            # Migration finished
            STR_MIGRATION_FINISHED = 'Live Migration Finished: '
            if log.logMessage.startswith(STR_MIGRATION_FINISHED):
                msg = log.logMessage[len(STR_MIGRATION_FINISHED):]
                migration = json.loads(msg)
                successful.append(migration)
            
            # Migration failed
            STR_MIGRATION_FAILED = 'Live Migration Failed: '
            if log.logMessage.startswith(STR_MIGRATION_FAILED):
                msg = log.logMessage[len(STR_MIGRATION_FAILED):]
                migration = json.loads(msg)
                failed.append(migration)
                
            # Server empty
            STR_ACTIVE_SERVERS = 'Active Servers: '
            if log.logMessage.startswith(STR_ACTIVE_SERVERS):
                msg = log.logMessage[len(STR_ACTIVE_SERVERS):]
                active = json.loads(msg)
                active_state = (log.timestamp, active['count'], active['servers'])
                server_active.append(active_state)
                
    return successful, failed, server_active

'''
Extracts all JSON configuration and metric information from the Rain log. This
method only works this the most recent version of Rain dumps!
'''
def __fetch_rain_data(connection, load_host, timeframe):
    # Configuration
    schedule = None
    track_config = None
    stopped = False
    
    # Metrics
    global_metrics = None
    rain_metrics = []
    track_metrics = []
    spec_metrics = []
    errors = []
     
    # Build query
    query = ttypes.LogsQuery()
    query.hostname = load_host
    query.sensor = 'rain'
    query.startTime = timeframe[0]
    query.stopTime = timeframe[1]
    logs = connection.queryLogs(query)
    
    # scan logs for results
    for log in logs:
        if log.timestamp > (timeframe[1] + 5 * 60) * 1000:
            print 'skipping remaining log messages - out of timeframe'
            break

        # Track schedule
        STR_BENCHMARK_SCHEDULE = 'Schedule: '
        if log.logMessage.startswith(STR_BENCHMARK_SCHEDULE):
            msg = log.logMessage[len(STR_BENCHMARK_SCHEDULE):]
            schedule = json.loads(msg)
            schedule = (schedule['startSteadyState'], schedule['endSteadyState'])
        
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
            
        # Read global metrics
        STR_GLOBAL_METRICS = 'Global metrics: '
        if log.logMessage.startswith(STR_GLOBAL_METRICS):
            msg = log.logMessage[len(STR_GLOBAL_METRICS):]
            global_metrics = json.loads(msg)
            
        # Read track metrics
        STR_TRACK_METRICS = 'Track metrics: '
        if log.logMessage.startswith(STR_TRACK_METRICS):
            msg = log.logMessage[len(STR_TRACK_METRICS):]
            data = json.loads(msg)
            track_metrics.append(data)
            
        # Read specj metrics
        STR_DEALER_METRICS = 'Dealer metrics: '
        if log.logMessage.startswith(STR_DEALER_METRICS):
            msg = log.logMessage[len(STR_DEALER_METRICS):]
            data = json.loads(msg)
            spec_metrics.append(data)
            
        # Read MFG metrics
        STR_MFG_METRICS = 'Mfg metrics: '
        if log.logMessage.startswith(STR_MFG_METRICS):
            msg = log.logMessage[len(STR_MFG_METRICS):]
            data = json.loads(msg)
            spec_metrics.append(data) 
        
        # Read MFG metrics
        STOP = 'Rain stopped'
        if log.logMessage.startswith(STOP):
            msg = log.logMessage[len(STOP):]
            stopped = True
           
        # Extract errors
        if log.logLevel == 40000:
            errors.append(log.logMessage)   
        
    if stopped == False:
        __warn('Missing "Rain Stopped" message')
        
    return schedule, track_config, global_metrics, rain_metrics, track_metrics, spec_metrics, errors 


'''
Fetch a timeseries
'''
def __fetch_timeseries(connection, host, sensor, timeframe):
    query = ttypes.TimeSeriesQuery()
    query.hostname = host
    query.startTime = timeframe[0]
    query.stopTime = timeframe[1]
    query.sensor = sensor
    
    result = connection.query(query)
    time, result = util.to_array_collector(result, timeframe)
        
    return result, time


'''
Convert a datetime from a string to a UNIX timestamp
'''
def __to_timestamp(date):
    res = time.strptime(date, '%d/%m/%Y %H:%M:%S')    
    return int(time.mktime(res))


'''
Dump all elements from a tupel as a CSV row
'''
def __dump_elements(elements, title=None, separator=', '):
    if title is not None:
        __dump_elements(title)
    
    result = ['%s' for _ in xrange(len(elements))]
    result = separator.join(result)
    print result % elements


'''
Dump the contents of a scorecard
'''
def __dump_scorecard(scoreboard, title=True, prefix_dump=None, prefix_data=None):
    dump = ('track', 'interval_duration', 'total_ops_successful', 'max_response_time', 'average_response_time', 'min_response_time', 'effective_load_ops', 'effective_load_req', 'total_operations_failed')
    data = []
    for element in dump:
        try:
            value = scoreboard[element]
            data.append(str(value))
        except:
            pass

    # Prefix
    if prefix_dump != None and prefix_data != None:
        prefix_dump = list(prefix_dump)
        prefix_dump.extend(dump)
        dump = prefix_dump
        prefix_data.extend(data)
        data = prefix_data
        
    if title:
        __dump_elements(tuple(data), tuple(dump))
    else:
        __dump_elements(tuple(data))

'''
Dump the contents of a scoreboard
'''
def __dump_scoreboard(track, title=True):
    dump = ('target_host',)
    data = []
    for element in dump:
        value = track[element]
        data.append(str(value))
    
    __dump_scorecard(track['final_scorecard'], title, dump, data)

'''
Dump the contents of a spec metric
'''
def __dump_spec(spec, title=True):
    dealer = ('track', 'description', 'Purchase: Average Vehicles per Order', 'Purchase: Vehicle Purchasing Rate (/sec)', 'Purchase: Large Order Purchasing Rate (/sec)',
            'Purchase: Large Order Vehicle Purchasing Rate (/sec)', 'Purchase: Regular Order Vehicle Purchasing Rate (/sec)', 'Purchase: Immediate Order Purchasing Rate (/sec)',
            'Purchase: Deferred Orders Purchasing Rate (/sec)', 'Purchase: Cart Clear Rate (/sec)', 'Purchase: Order Line Rate removed from Cart (/sec)',
            'Purchase: Bad Credit Rate (/sec)', 'Manage: Deferred Orders cancelled (/sec)', 'Manage: Vehicles sold from lot (/sec)', 'Browse: forwards (/sec)',
            'Browse: backwards (/sec)')
    
    mfg = ('track', 'description', 'EJB Planned Line Production Rate (/sec)', 'WS Planned Line Production Rate (/sec)', 'EJB Planned Line Vehicle Production Rate (/sec)',
           'WS Planned Line Vehicle Production Rate (/sec)')
    
    # Use keys of dealer or mfg result
    dump = None
    if spec[0]['result'] == 'DealerMetrics':
        dump = dealer
    elif spec[0]['result'] == 'MfgMetrics':
        dump = mfg
    else:
        return
    
    # Transform results into map
    mapping = {}
    for block in spec:
        descr = block['description']
        if block.has_key('result'):
            result = block['result']
            
        if mapping.has_key(descr) == False:
            mapping[descr] = result
            
    # Extract results and print csv row
    data = []
    for element in dump:
        value = mapping[element]
        data.append(str(value))
        
    if title:
        __dump_elements(tuple(data), dump)
    else:
        __dump_elements(tuple(data))
 
def __dump_metrics(global_metrics, rain_metrics, track_metrics, spec_metrics):
    print '## GLOBAL METRICS ###'
    first = True
    for global_metric in global_metrics:
        # __dump_scorecard(global_metric, first)
        first = False
        
    for metric in rain_metrics:
        pass
        # __dump_scorecard(metric, first) 
        
    print '## TRACK METRICS ##'
    first = True
    for track in track_metrics:
        # __dump_scoreboard(track, first)
        first = False
            
    print '## SPEC METRICS ##'
    for spectype in ('DealerMetrics', 'MfgMetrics'):
        first = True 
        for spec in spec_metrics:
            if spec[0]['result'] != spectype: continue
            # __dump_spec(spec, first)
            first = False
            
 
def __processing_generate_profiles(domain_workload_map, cpu):
    for domain in domain_workload_map.keys():
        workload = domain_workload_map[domain]
        workload = workload.replace(profiles.POSTFIX_USER, '')
        print 'domain: %s workload: %s' % (domain, workload)
        
        if TRACE_EXTRACT:
            # Ensure that this is really the users intention!
            test = raw_input('Extracting traces will overwrite data in Times (yes/no)? ')
            if test != 'yes':
                print 'Cancelled'
                break
            
            # Create profile from CPU load
            profiles.process_sonar_trace(workload, cpu[domain][0], cpu[domain][1], True)
 
def __analytics_migrations(data_frame, cpu, mem, migrations, server_active_flags):
    migration_durations = []
    for migration in migrations:
        migration_durations.append(migration['duration'])
    print 'Average migration time: %f' % np.mean(migration_durations)
    
    last_state = None
    
    occupied_minutes = 0.0
    empty_minutes = 0.0
    
    _clean_cpu = []
    _clean_mem = []
    
    _server_active = []
    _server_active.append((data_frame[0], server_active_flags[0][1], server_active_flags[0][2]))
    _server_active.extend(server_active_flags)
    _server_active.append((data_frame[1], server_active_flags[-1][1], server_active_flags[-1][2]))
    
    for state in _server_active:
        if last_state == None:
            last_state = state
            continue
        
        delta_time = float(state[0] - last_state[0])
        
        # minutes - timestamps are in seconds
        # last state server count is used:
        # |FLAG (last) | ........ |FLAG (iteration current) |
        # The info from the last flag was active due to the time stamp
        # of the iteration current flag!
        active_servers = float(last_state[1])
        
        occupied_minutes += (active_servers * delta_time) / 60.0 
        empty_minutes += (delta_time * (len(nodes.HOSTS) - active_servers)) / 60
        
        for srv in nodes.NODES: 
            def extract(tupel):
                _sub_arr = []
                for i in xrange(len(tupel[1])):
                    value = tupel[0][i]
                    time = tupel[1][i]
                    
                    if time >= last_state[0] and time <= state[0]:
                        _sub_arr.append(value)
                        
                return _sub_arr
            
            _sub_cpu = extract(cpu[srv])
            _sub_mem = extract(mem[srv])
            
            # if np.mean(_sub_cpu) > 3: 
            if srv in last_state[2]:
                # Checked calculation by sighting TS data - seems to work 
                #from datetime import datetime
                #f = lambda i: datetime.fromtimestamp(i).strftime('%H:%M:%S') 
                #print 'SRV %s FRAME: %s - %s' % (srv, f(last_state[0]), f(state[0]))  
                _clean_cpu.extend(_sub_cpu)
                _clean_mem.extend(_sub_mem)
            
        
        last_state = state
    
    duration = float(data_frame[1] - data_frame[0]) / 60.0 / 60.0
    print 'Duration: %i' % (duration * 60 * len(nodes.HOSTS))
    print 'Duration check: %i' % (occupied_minutes + empty_minutes)
    print 'Occupied minutes: %i' % occupied_minutes
    print 'Empty minutes: %i' % empty_minutes
    print 'Average servers: %f' % (occupied_minutes / 60 / duration)
    
    print 'Average server load: %f' % np.mean(_clean_cpu)
    avg_cpu = np.mean(_clean_cpu)
    avg_mem = np.mean(_clean_mem)
    avg_servers = occupied_minutes / 60 / duration
    
    return avg_servers, avg_cpu, avg_mem
    
    
 
def __analytics_server_utilization(cpu, mem):
    # This approach does only work for static allocations. For dynamic allocations 
    # the _cpu and _mem values are updated by the migration analytics!
    dump = ('node', 'cpu, mem')
    __dump_elements(dump)
    
    _total_cpu = []
    _total_mem = []
    for srv in nodes.NODES: 
        _cpu = np.mean(cpu[srv][0])
        _mem = np.mean(mem[srv][0])
        
        if _cpu > 3: # do not include offline servers
            _total_cpu.extend(cpu[srv][0])
            _total_mem.extend(mem[srv][0])
        
        data = [srv, _cpu, _mem]
        __dump_elements(tuple(data))
        
    _cpu = np.mean(_total_cpu) # are updated by migration analytics
    _mem = np.mean(_total_mem) # are updated by migration analytics
    
    data = ['total', _cpu, _mem]
    __dump_elements(tuple(data))
    
    return _cpu, _mem
 
def __analytics_global_aggregation(global_metrics, servers, avg_cpu, avg_mem, sla_fail_count, migration_count):
    global_metric_aggregation = {}
    
    # Define the elements to aggregate and the aggregation function
    # x = a tuple of two values: (aggregated value, temporary value like a counter)
    # y = the new value which is added to the aggregation
    agg_desc = {
                'total_ops_successful' : lambda x, y: (x[0] + y, 0),
                'max_response_time' : lambda x, y: (max(x[0], y), 0),
                'average_response_time': lambda x, y: ((x[0] * x[1] + y) / (x[1] + 1), x[1] + 1),
                'min_response_time' : lambda x, y: (min(x[0], y), 0),
                'effective_load_ops' : lambda x, y: (x[0] + y, 0),
                'effective_load_req': lambda x, y: (x[0] + y, 0),
                'total_operations_failed' : lambda x, y: (x[0] + y, 0),
                }
    
    # Iterate over all global results
    for global_metric in global_metrics:
        # For each element in the global result
        for element in agg_desc.keys():
            # Get the element value
            value1 = global_metric[element]
            
            # Get the aggregated element value 
            if global_metric_aggregation.has_key(element) == False: global_metric_aggregation[element] = (0, 0)
            value0 = global_metric_aggregation[element]
            
            # Run aggregation
            global_metric_aggregation[element] = agg_desc[element](value0, value1)

    # Add other stuff to the global metric
    global_metric_aggregation['server_count'] = (servers, 0)
    global_metric_aggregation['cpu_load'] = (avg_cpu, 0)
    global_metric_aggregation['mem_load'] = (avg_mem, 0)
    global_metric_aggregation['total_response_time_threshold'] = (sla_fail_count, 0)
    global_metric_aggregation['migrations_successful'] = (migration_count, 0)

    dump = ('server_count', 'cpu_load', 'mem_load', 'total_ops_successful', 'total_operations_failed', 'average_response_time',
             'max_response_time', 'effective_load_ops', 'effective_load_req', 'total_response_time_threshold',
             'migrations_successful')
    data = []
    for element in dump:
        try:
            value = global_metric_aggregation[element][0]
            data.append(str(value))
        except: 
            print 'Error in %s' % element
    __dump_elements(tuple(data), dump, separator='\t')   

def connect_sonar(connection):
    # Dump the configuration
    __dump_configuration()
    
    # Configure experiment
    start = __to_timestamp(START)
    stop = __to_timestamp(END)
    raw_frame = (start, stop)
    
    # Get sync markers from control (start of driving load)
    sync_markers = __fetch_start_benchamrk_syncs(connection, CONTROLLER_NODE, raw_frame)
    print '## SYNC MARKERS ##'
    __dump_elements(sync_markers)
    
    # Estimate sync markers if no sync markers where found
    if sync_markers[0] is None:
        __warn('Sync marker not found')
        sync_markers = (raw_frame[0], sync_markers[1], sync_markers[2])
    
    #####################################################################################################################################
    ### Reading Allocation ##############################################################################################################
    #####################################################################################################################################
    allocation_frame = (sync_markers[0], raw_frame[1])
    servers, assignment, migrations, placement, matrix = __fetch_allocation_config(connection, CONTROLLER_NODE, allocation_frame)
    print '## ALLOCATION ##'
    print 'Placement Strategy: %s' % placement
    print 'Number of servers %i' % servers
    print 'Assignment: %s' % assignment
    print 'Migrations: %s' % migrations
    print 'Service matrix: %s' % matrix
    
    #####################################################################################################################################
    ### Reading Results from Rain #######################################################################################################
    #####################################################################################################################################
    _schedules = []
    _track_configs = []
    _global_metrics = []
    _rain_metrics = []
    _track_metrics = []
    _spec_metrics = []
    _errors = []
    
    # Fetch rain data
    for host in DRIVER_NODES:
        print 'Fetching driver node: %s ...' % host
        rain_data = __fetch_rain_data(connection, host, raw_frame)
        schedule, track_config, global_metrics, rain_metrics, track_metrics, spec_metrics, errors = rain_data
        
        if schedule is not None: _schedules.append(schedule)
        if track_config is not None: _track_configs.append((track_config, host))
        if global_metrics is not None: _global_metrics.append(global_metrics)
        if rain_metrics is not None: _rain_metrics.extend(rain_metrics)
        if track_metrics is not None: _track_metrics.extend(track_metrics)
        if spec_metrics is not None: _spec_metrics.extend(spec_metrics)
        if errors is not None: _errors.extend(errors)
        
    # Print metrics
    __dump_metrics(_global_metrics, _rain_metrics, _track_metrics, _spec_metrics)
        
    print '## ERRORS ##'
    for error in _errors:
        if error == 'Audit failed: Incorrect value for steadyState, should be 3600':
            # print 'expected> ', error
            pass
        elif error.find('Oops: Uncaught exception caused thread:') != -1:
            print 'critical> ', error
            __warn(error)
        else:
            if len(error) < 100: print error
            else: print error[0:100]
        
    print '## SCHEDULE ##'
    # Each rain driver logs an execution schedule which defines the timestamp to start the
    # steady state phase and to end it
    schedule_starts = []
    schedule_ends = []
    for schedule in _schedules:
        schedule_starts.append(schedule[0])
        schedule_ends.append(schedule[1])
        __dump_elements(schedule)
       
    # refine data raw_frame with schedules
    print '## REFINED TIME FRAME ##'
    data_frame = (max(schedule_starts) / 1000, min(schedule_ends) / 1000)
    __dump_elements(data_frame)
    duration = float(data_frame[1] - data_frame[0]) / 60.0 / 60.0
    print 'Frame duration is: %f hours' % (duration)
    
    print '## DOMAIN WORKLOAD MAPS (TRACK CONFIGURATION) ##'
    # Results
    domains = []
    domain_track_map = {}
    domain_workload_map = {}
    
    for track_config, source_host in _track_configs:
        for track in track_config:
            host = track_config[track]['target']['hostname']
            workload = track_config[track]['loadScheduleCreatorParameters']['profile']
            
            if host not in domains:
                domains.append(host)
            
            if domain_track_map.has_key(host) == False:
                domain_track_map[host] = []
            domain_track_map[host].append((source_host, track))
    
            if domain_workload_map.has_key(host) == False:
                domain_workload_map[host] = workload
            else:
                if domain_workload_map[host] != workload:
                    print 'WARN: Multiple load profiles on the same target'
                    
    # print 'domain track map: %s' % domain_track_map
    # print 'domain workload map: %s' % domain_workload_map

    print '## RESPONSE TIME THRESHOLD CHECK ###'
    # Fetch track response time and calculate average
    sla_fail_count = 0
    for key in domain_track_map.keys():
        for track in domain_track_map[key]:
            res_resp, _ = __fetch_timeseries(connection, track[0], 'rain.rtime.%s' % track[1], data_frame)
            # 3 Second response time "User Preferences and Search Engine Latency" by Jake D. et al.  
            cond = res_resp > 3000 
            ext = np.extract(cond, res_resp)
            sla_fail_count += len(ext)
    print 'SLA fail count: %i' % sla_fail_count
    
    #####################################################################################################################################
    ### Reading Migrations ##############################################################################################################
    #####################################################################################################################################
    migrations_successful, migrations_failed, server_active_flags = __fetch_migrations(connection, CONTROLLER_NODE, data_frame)
    
    print '## MIGRATIONS ##'
    print 'Successful: %i' % len(migrations_successful)
    print 'Failed: %i' % len(migrations_failed)
    
    #####################################################################################################################################
    ### Resource Readings ###############################################################################################################
    #####################################################################################################################################
    
    # Results
    cpu = {}
    mem = {}
    
    print '## FETCHING CPU LOAD SERVERS ... ##'
    for srv in nodes.NODES:
        res_cpu, tim_cpu = __fetch_timeseries(connection, srv, 'psutilcpu', data_frame)
        res_mem, tim_mem = __fetch_timeseries(connection, srv, 'psutilmem.phymem', data_frame)
        cpu[srv] = (res_cpu, tim_cpu)
        mem[srv] = (res_mem, tim_mem)
    
    print '## FETCHIN CPU LOAD DOMAINS ... ##'
    for domain in domains:
        res_cpu, tim_cpu = __fetch_timeseries(connection, domain, 'psutilcpu', data_frame)
        res_mem, tim_mem = __fetch_timeseries(connection, domain, 'psutilmem.phymem', data_frame)
        cpu[domain] = (res_cpu, tim_cpu)
        mem[domain] = (res_mem, tim_mem)
    
    # Generate and write CPU profiles to Times
    print '## GENERATING CPU LOAD PROFILES ##'
    if TRACE_EXTRACT:
        raw_input('Press a key to continue generating profiles:')
        __processing_generate_profiles(domain_workload_map, cpu)
        
    #####################################################################################################################################
    ### Analysis ########################################################################################################################
    #####################################################################################################################################
    # Updates values from the extraction phase
    #####################################################################################################################################
    
    print '## AVG CPU,MEM LOAD ##'
    # This approach does only work for static allocations. For dynamic allocations 
    # the _cpu and _mem values are updated by the migration analytics!
    avg_cpu, avg_mem = __analytics_server_utilization(cpu, mem)
    
    print '## MIGRATIONS ##'
    if migrations_successful: 
        servers, avg_cpu, avg_mem = __analytics_migrations(data_frame, cpu, mem, migrations_successful, server_active_flags)
    else:
        print 'No migrations'
    
    print '## GLOBAL METRIC AGGREGATION ###'
    __analytics_global_aggregation(_global_metrics, servers, avg_cpu, avg_mem,
                                   sla_fail_count, len(migrations_successful))
    
    
    # Dump all warnings
    __dump_warns()


if __name__ == '__main__':
    connection = __connect()
    try:
        connect_sonar(connection)
    except:
        traceback.print_exc(file=sys.stdout)
    __disconnect()
