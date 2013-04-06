from collector import CollectService, ManagementService, ttypes
from datetime import datetime
from scipy import stats as sps
from service import times_client
from subprocess import Popen, PIPE
from threading import Thread
from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport
from times import ttypes as times_ttypes
from virtual import nodes
from workload import profiles, util, plot as wplot
import configuration
import csv
import json
import math
import matplotlib.pyplot as plt
import numpy as np
import sys
import time
import traceback

'''
Additional R-Scripts:
linearModel.R
migrationAnalysis.R
'''

##########################
# # Configuration        ##
##########################
COLLECTOR_IP = 'monitor0'
MANAGEMENT_PORT = 7931
LOGGING_PORT = 7921
DEBUG = False
TRACE_EXTRACT = False
DRIVERS = 2
EXPERIMENT_DB = configuration.path('experiments', 'csv')

CONTROLLER_NODE = 'Andreas-PC'
DRIVER_NODES = ['load0', 'load1']

RAW = '19/03/2013 16:50:00    19/03/2013 23:50:00'
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
    query.startTime = frame[0] - 60 * 60  # Scan 10 minutes before the start_benchmark
    query.stopTime = frame[0] + 1 * 60  # Cannot occur after the benchmark start. Due to testing there may 
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
        print log
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
    query.startTime = timeframe[0] - 60
    query.stopTime = timeframe[1]
    logs = connection.queryLogs(query)
    
    # Sync marker load balancer release
    sync_release = None
    
    # List of migrations
    successful = []
    failed = []
    server_active = [] 
    triggered = []
    
    # Initial model
    initial = None
    
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
            # Initial model
            STR_INITIAL_MODEL = 'Controller Initial Model: '
            if log.logMessage.startswith(STR_INITIAL_MODEL):
                msg = log.logMessage[len(STR_INITIAL_MODEL):]
                initial = json.loads(msg)
            
            # Migration triggered
            STR_MIGRATION_TRIGGERED = 'Live Migration Triggered: '
            if log.logMessage.startswith(STR_MIGRATION_TRIGGERED):
                log.logMessage[len(STR_MIGRATION_TRIGGERED):]
                msg = log.logMessage[len(STR_MIGRATION_TRIGGERED):]
                migration = json.loads(msg)
                triggered.append((log.timestamp, migration)) 
            
            # Migration finished
            STR_MIGRATION_FINISHED = 'Live Migration Finished: '
            if log.logMessage.startswith(STR_MIGRATION_FINISHED):
                msg = log.logMessage[len(STR_MIGRATION_FINISHED):]
                migration = json.loads(msg)
                successful.append((log.timestamp, migration))
            
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
                
    return successful, failed, server_active, triggered, initial

'''
Extracts all JSON configuration and metric information from the Rain log. This
method only works this the most recent version of Rain dumps!
'''
def __fetch_rain_data(connection, load_host, timeframe):
    # Configuration
    schedule = None
    track_config = None
    stopped = False
    scenario_start = None
    
    # Metrics
    global_metrics = None
    rain_metrics = []
    track_metrics = []
    spec_metrics = []
    errors = []
    error_data = []
     
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
        
        # Read scenario start 
        STR_START_SCENARIO = 'Starting scenario (threads)'
        if log.logMessage.startswith(STR_START_SCENARIO):
            msg = log.logMessage[len(STR_START_SCENARIO):]
            scenario_start = log.timestamp
        
        # Read MFG metrics
        STOP = 'Rain stopped'
        if log.logMessage.startswith(STOP):
            msg = log.logMessage[len(STOP):]
            stopped = True
           
        # Extract errors
        if log.logLevel == 40000:
            errors.append(log.logMessage)
            error_data.append(log)   
        
    if stopped == False:
        __warn('Missing "Rain Stopped" message')
        
    return schedule, track_config, global_metrics, rain_metrics, track_metrics, spec_metrics, errors, scenario_start, error_data 


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
 
 
def __plot_migrations_vs_resp_time(data_frame, domain_track_map, migrations_triggered, migrations_successful):
    for domain in domain_track_map.keys():
        # New figure
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlabel('Time in seconds')
        ax.set_ylabel('Response time in milliseconds')

        # Plot response times        
        for track in domain_track_map[domain]:
            res_resp, res_time = __fetch_timeseries(connection, track[0], 'rain.rtime.%s' % track[1], data_frame)
            
            ax.plot(res_time, res_resp)
            
        # Add annotations to the trace
        for mig in migrations_triggered:
            if mig[1]['domain'] == domain:
                ax.axvline(mig[0], color='r')
       
        for mig in migrations_successful:
            if mig[1]['domain'] == domain: 
                ax.axvline(mig[0], color='g')

        plt.show()            
        # plt.savefig(configuration.path('migration_%s' % domain, 'pdf'))
            
 
def __plot_load_vs_servers(data_frame, cpu, mem, server_active_flags, domains):
    delta = 60
    
    sum_cpu_loads = []
    for t in xrange(data_frame[0], data_frame[1], delta):
        sum_cpu_load = 0
        # Get load from all nodes
        for node in nodes.NODES:
            
            # Get all data in time frame described by delta
            values = [0]
            for i in xrange(len(cpu[node][1])):
                time = cpu[node][1][i]
                load = cpu[node][0][i]
                if time > t and time < (t + delta):
                    values.append(load)
                    
            # Update global cpu load counter
            sum_cpu_load += np.max(values)
             
        sum_cpu_loads.append(sum_cpu_load)
    
    # New plot
    fig = plt.figure()
    
    # Plot accumulated CPU load
    ax = fig.add_subplot(111)
    ax.set_xlim(data_frame)
    ax.set_ylabel('Accumulated server load')
    ax.set_xlabel('Time hour:minutes')
    wplot.ticks(ax, wplot.to_hour, data_frame[0], data_frame[1])
    ax.plot(range(data_frame[0], data_frame[1], delta), sum_cpu_loads, label='Server Load')

    # Plot server active flags
    times = []
    data = []
    # Initial
    times.append(data_frame[0])
    data.append(len(nodes.NODES))
    # Server active flags
    for mig in server_active_flags:
        times.append(mig[0])
        data.append(mig[1])
    # Final
    times.append(data_frame[1])
    data.append(data[-1])
    
    ax2 = ax.twinx()
    ax2.set_ylabel('Number of active servers')
    ax2.set_ylim([0, len(nodes.NODES) + 1])
    ax2.set_xlim(data_frame)
    wplot.ticks(ax2, wplot.to_hour, data_frame[0], data_frame[1])
    ax2.step(times, data, color='red', ls='solid', label='Controller')
    
    # Plot lower bound
    times = []
    data = []
    for i, t in enumerate(xrange(data_frame[0], data_frame[1], delta)):
        times.append(t)
        data.append(math.ceil(sum_cpu_loads[i] / 100))
    # ax2.step(times, data, color='black', ls='dashed', label='Lower Bound')
    
    
    # Plot SSAP optimized (5 minutes)
    delta = 5 * 60
    times = xrange(data_frame[0], data_frame[1], delta)
    data = []
    # Aggregate load for all time frames
    for t in xrange(data_frame[0], data_frame[1], delta):
        
        # Get load for each domain in this frame
        domain_loads = []
        for domain in domains:
            ni = []
            for i in xrange(len(cpu[domain][1])):
                tim = cpu[domain][1][i]
                ld = cpu[domain][0][i]
                if tim > t and tim < (t + delta):
                    ni.append(ld)
            domain_loads.append(np.percentile(ni, 95))
            
        # Solve
        from ipmodels import ssap
        _, count = ssap.solve(nodes.count(), 100 * nodes.cpu_factor(), domain_loads)
        data.append(count)
        
    ax2.step(times, data, color='green', ls='-.', label='SSAP')

    # plt.savefig(configuration.path('servers_load', 'pdf'))
    plt.show()

 
def __plot_migrations(cpu, mem, migrations_triggered, migrations_successful):
    for node in nodes.NODES:
        # Node memory consumption
        node_memory = mem[node]
        node_cpu = cpu[node]
        
        # Plot node memory        
        fig = plt.figure()
        ax = fig.add_subplot(111)
        
        ax2 = ax.twinx()
        ax2.plot(node_cpu[1], node_cpu[0], c='gray', linewidth=0.05)
        
        ax.axis([min(node_memory[1]), max(node_memory[1]), 0, 100])
        ax.plot(node_memory[1], node_memory[0])
                
        # Plot migration start
        for mig in migrations_triggered:
            if mig[1]['from'] == node:
                ax.axvline(mig[0] + 40, color='r')
                
            if mig[1]['to'] == node:
                ax.axvline(mig[0] + 40, color='c')
       
       
        # Plot migration end and annotations
        annotation_offset = 10
        for mig in migrations_successful: 
            annotation_offset = (annotation_offset + 10) % 90
            
            if mig[1]['from'] == node:
                ax.axvline(mig[0] + 40, color='r')
                
                ax.annotate('%is' % mig[1]['duration'], xy=(mig[0], annotation_offset), xycoords='data',
                xytext=(-50, -30), textcoords='offset points',
                arrowprops=dict(arrowstyle="->",
                                connectionstyle="arc3,rad=.2"),
                )
                
            if mig[1]['to'] == node:
                ax.axvline(mig[0] + 40, color='c')
                
                ax.annotate('%is' % mig[1]['duration'], xy=(mig[0], annotation_offset), xycoords='data',
                xytext=(-50, -30), textcoords='offset points',
                arrowprops=dict(arrowstyle="->",
                                connectionstyle="arc3,rad=.2"),
                )

        # Show plot        
        plt.show()
   
   
'''
Extracts CPU usage before and during each successful migration
'''
def __analytics_migration_overheads(data_frame, cpu, migrations_successful):
    # Iterate over all migrations
    for migration in migrations_successful:
        # time shift
        time_migration_end = migration[0]
        time_migration_start = migration[0] - migration[1]['duration']
        
        def extract_cpu(cpu_load):
            readings_before, readings_during = [], []
            
            for i in xrange(len(cpu_load[0])):
                time = cpu_load[1][i]
                load = cpu_load[0][i]
                
                if time > time_migration_start and time < time_migration_end:
                    readings_during.append(load)
                    
                elif time > (time_migration_start - 60) and time < time_migration_start:
                    readings_before.append(load)
                    
            return readings_before, readings_during 


        source_server = migration[1]['from']
        target_server = migration[1]['to']
        cpu_load_source = cpu[source_server]
        cpu_load_target = cpu[target_server]
        
        before_cpu_source, during_cpu_source = extract_cpu(cpu_load_source)
        before_cpu_target, during_cpu_target = extract_cpu(cpu_load_target)
        
        result = (np.mean(before_cpu_source), np.mean(during_cpu_source),
                 np.mean(before_cpu_target), np.mean(during_cpu_target), float(migration[1]['duration']))
        print 'source: before=%0.2f during=%0.2f    target: before=%0.2f during=%0.2f    duration:%0.2f' % result
        
 
def __analytics_migrations(data_frame, cpu, mem, migrations, server_active_flags):
    # Calculate descriptive statistics on migration time
    migration_durations = []
    for migration in migrations:
        migration_durations.append(migration[1]['duration'])

    print 'Migration time average: %f' % np.mean(migration_durations)
    print 'Migration time 50th percentile: %f' % np.percentile(migration_durations, 50)
    print 'Migration time 90th percentile: %f' % np.percentile(migration_durations, 90)
    print 'Migration time 99th percentile: %f' % np.percentile(migration_durations, 99)
    
    min_servers = sys.maxint
    max_servers = 0
    for active in server_active_flags:
        min_servers = min(min_servers, active[1])
        max_servers = max(max_servers, active[1])
    print 'Min servers: %i' % min_servers
    print 'Max servers: %i' % max_servers
    
    # Average server count and server load calculations
    # Server active flags mark changes in server active count
    # Wrap server active flags with start and end flag at the beginning and end of experiment
    # Each state is a tuple with: 
    _server_active = []
    _server_active.append((data_frame[0], server_active_flags[0][1], server_active_flags[0][2]))
    _server_active.extend(server_active_flags)
    _server_active.append((data_frame[1], server_active_flags[-1][1], server_active_flags[-1][2]))

    # Hold info about the state of the last iteration interval
    last_state = None
    
    # Counts occupied and empty server minutes
    occupied_minutes = 0.0
    empty_minutes = 0.0
    
    # List of cpu and mem readings for busy server time intervals only
    # Non active server readings are excluded from these lists 
    _clean_cpu = []
    _clean_mem = []

    # Iterate over all server status state changes    
    for state in _server_active:
        # If last state is not set - this is the last state
        if last_state == None:
            last_state = state
            continue
        
        # Time between last state and current state
        delta_time = float(state[0] - last_state[0])
        
        # Number of active servers 
        # |FLAG (last) | ........ |FLAG (iteration current) |
        # Servers active: 
        # |                       ..........................|
        # |.......................                          |
        # |^^^this one is taken^^^
        # The info from the *last flag* was active due *to the iteration current time stamp*
        active_servers = float(last_state[1])
        
        # Occupied server minutes
        occupied_minutes += (active_servers * delta_time) / 60.0
        
        # Empty server minutes 
        empty_minutes += (delta_time * (len(nodes.NODES) - active_servers)) / 60
        
        # Go over all servers
        for srv in nodes.NODES:
            # Extracts a segment of a load time series
            # Parameter: tuple with (load TS, time TS) 
            def extract(tupel):
                _sub_arr = []
                # Go over all timestamps
                for i in xrange(len(tupel[1])):
                    value = tupel[0][i]
                    time = tupel[1][i]
                    
                    # Check if time is in range (timestamp of last state and timestamp of current state)
                    if time >= last_state[0] and time < state[0]:
                        _sub_arr.append(value)
                        
                # Return segment
                return _sub_arr
            
            # Get the cpu and mem load of the server during the delta_time interval
            _sub_cpu = extract(cpu[srv])
            _sub_mem = extract(mem[srv])
            
            # If the server was active in the interval - add the loads to the total load
            if srv in last_state[2]:
                # Checked calculation by sighting TS data - seems to work 
                _clean_cpu.extend(_sub_cpu)
                _clean_mem.extend(_sub_mem)
            
        # Update last_state!
        last_state = state
    
    # Calculate experiment duration in hours as float
    duration = float(data_frame[1] - data_frame[0]) / 60.0 / 60.0
    
    # Calculate average loads
    avg_cpu = np.mean(_clean_cpu)
    avg_mem = np.mean(_clean_mem)
    avg_servers = (occupied_minutes / 60.0) / duration
    
    # Print stats
    print 'Duration: %i' % (duration * 60 * len(nodes.NODES))
    print 'Duration check: %i' % (occupied_minutes + empty_minutes)
    print 'Occupied minutes: %i' % occupied_minutes
    print 'Empty minutes: %i' % empty_minutes
    print 'Average servers: %f' % (occupied_minutes / 60 / duration)
    print 'Average server load: %f' % np.mean(_clean_cpu)
    
    # Return analytical results
    return avg_servers, avg_cpu, avg_mem, min_servers, max_servers
    
 
def __analytics_server_utilization(cpu, mem):
    # This approach does only work for static allocations. For dynamic allocations 
    # the _cpu and _mem values are updated by the migration analytics!
    dump = ('node', 'cpu, mem')
    __dump_elements(dump)
    
    _total_cpu = []
    _total_mem = []
    _violations = 0
    for srv in nodes.NODES: 
        _cpu = np.mean(cpu[srv][0])
        _mem = np.mean(mem[srv][0])
        
        if _cpu > 3:  # do not include offline servers
            _total_cpu.extend(cpu[srv][0])
            _total_mem.extend(mem[srv][0])
        
        data = [srv, _cpu, _mem]
        __dump_elements(tuple(data))
        
        _violations += len(cpu[srv][0][cpu[srv][0] > 99])
         
        
    _cpu = np.mean(_total_cpu)  # are updated by migration analytics
    _mem = np.mean(_total_mem)  # are updated by migration analytics
    
    data = ['total', _cpu, _mem]
    __dump_elements(tuple(data))
    
    return _cpu, _mem, _violations
 
 
def __analytics_global_aggregation(global_metrics, servers, avg_cpu, avg_mem, sla_fail_count,
                                   migration_count, min_nodes, max_nodes, srv_cpu_violations):
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
    print '### Operation Sampling Table ###'
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
            
        op = global_metric['operational']['operations']
        for o in op:
            print '%s \t %i \t %d \t %d' % (o['operation_name'], o['samples_seen'], o['sample_mean'], o['sample_stdev'])
        

    # Add other stuff to the global metric
    global_metric_aggregation['server_count'] = (servers, 0)
    global_metric_aggregation['cpu_load'] = (avg_cpu, 0)
    global_metric_aggregation['mem_load'] = (avg_mem, 0)
    global_metric_aggregation['total_response_time_threshold'] = (sla_fail_count, 0)
    global_metric_aggregation['migrations_successful'] = (migration_count, 0)
    global_metric_aggregation['min_nodes'] = (min_nodes, 0)
    global_metric_aggregation['max_nodes'] = (max_nodes, 0)
    global_metric_aggregation['srv_cpu_violations'] = (srv_cpu_violations, 0)

    dump = ('server_count', 'cpu_load', 'mem_load', 'total_ops_successful', 'total_operations_failed', 'average_response_time',
             'max_response_time', 'effective_load_ops', 'effective_load_req', 'total_response_time_threshold',
             'migrations_successful', 'min_nodes', 'max_nodes', 'srv_cpu_violations')
    data = []
    for element in dump:
        try:
            value = global_metric_aggregation[element][0]
            data.append(str(value))
        except: 
            print 'Error in %s' % element
    __dump_elements(tuple(data), dump, separator='\t')   

def __load_experiment_db(db_file):
    experiments = []
    header = False
    with open(db_file, 'rb') as db_file:
        dbreader = csv.reader(db_file, delimiter='\t')
        
        controller = None
        mix = None
        experiment_type = None
        crt = 0
        
        for row in dbreader:
            if header == False:
                header = True
                continue
            
            if row[2] == '*':
                controller = row[0]
                continue
            
            if row[0] != '':
                mix = row[0]
                
            if row[1] != '':
                crt = 0
                experiment_type = row[1]
            
            if row[5] != 'OK':
                continue
            
            if row[3] != '' and row[4] != '':
                date = row[3] + '    ' + row[4]
                experiments.append((date, controller, mix, experiment_type, crt, row[6:]))
                
                crt += 1
                
    return experiments


def __load_response_times(resp_times_file):
    lines = []
    with open(configuration.path('%s' % resp_times_file, 'csv'), 'rb') as resp_times_file:
        dbreader = csv.reader(resp_times_file, delimiter='\t')
        for line in dbreader:
            lines.append(line)
    return lines


def t_test(m1, m2, s1, s2, n1, n2):
    t = abs(m1 - m2) / math.sqrt((math.pow(s1, 2) / n1) + (math.pow(s2, 2) / n2))
    
    s12 = math.pow(s1, 2)
    s22 = math.pow(s2, 2)
    df = math.pow((s12 / n1 + s22 / n2), 2) / ((math.pow(s12 / n1, 2) / (n1 - 1)) + (math.pow(s22 / n2, 2) / (n2 - 1)))
    
    test = sps.t.ppf(0.975, df)
    
    return t, test, df


def t_test_response_statistics_all():
    
    mixes = ['MIX0', 'MIX1', 'MIX2', 'MIX0M', 'MIX1M', 'MIX2M']
    controllers = {
                  'Round Robin' : ['Default'],
                  'Optimization' : ['Underbooking', 'Overbooking', 'Default'],
                  'Reactive' : ['Default'],
                  'Proactive' : ['Default']
                  }
    runs = [0, 1, 2]

    class Hold:
        def __init__(self):
            self.samples = 1
            self.sum_rtime = 0
            self.sum_std = 0
            self.rtime = []
        
        def accept(self, samples, rtime, std):
            self.samples += samples
            self.sum_rtime += samples * rtime
            self.sum_std += samples * std
            self.rtime.append(rtime)
            
        def sd_rtime(self):
            return np.var(self.rtime)
            
        def average(self):
            self.sum_rtime /= self.samples
            self.sum_std /= self.samples
            
    def handle(mix, control0, type0, control1, type1):
        # Aggregate date
        r1 = Hold()
        r2 = Hold()
        
        # Aggregate all data across all runs
        for run in runs:
            file0 = '%s_%s_%s_%i' % (control0, mix, type0, run)
            file1 = '%s_%s_%s_%i' % (control1, mix, type1, run)
            
            if file0 == file1:
                # Do not compare the same files
                raise StopIteration()
            try:
                set0 = __load_response_times(file0)
                set1 = __load_response_times(file1)
            except:
                # File was not found - not important
                raise StopIteration()

            # Operations in the set are incompatible            
            if len(set0) != len(set1):
                __warn('Skipping invalid length %s' % (file0 + ' x ' + file1))
                raise StopIteration()
            
            # Iterate over all operations
            for i in xrange(len(set0)):
                operation0 = set0[i]
                operation1 = set1[i]
                
                # Samples
                n1 = float(operation0[1])
                n2 = float(operation1[1])
                
                # Sample mean
                m1 = float(operation0[2])
                m2 = float(operation1[2])
                
                # Sample std
                s1 = float(operation0[3])
                s2 = float(operation1[3])
                
                # Accumulate results
                r1.accept(n1, m1, s1)
                r2.accept(n2, m2, s2)
                
        # Compare controllers over all runs
        try:
            r1.average()
            r2.average()
            t, test, df = t_test(r1.sum_rtime, r2.sum_rtime, r1.sum_std, r1.sum_std,
                                 r1.samples, r2.samples)
            
            if r1.sd_rtime() < r2.sd_rtime():
                print r1.sd_rtime() / r2.sd_rtime()
            else:
                print r2.sd_rtime() / r1.sd_rtime()
            
            sig = t > test
            if sig:
                report = '%s.%s to %s.%s (%s) $p(%i)=%0.02f,p<0.05$' % (control0, type0, control1, type1, mix, df, t)
                print '%s.%s x %s.%s (%s) -> %i, t=%0.2f test=%0.2f df=%0.2f [%s]' % (control0, type0, control1, type1, mix, sig, t, test, df, report)
        except Exception as inst:
            print inst
            __warn('%s.%s x %s.%s -> %s' % (control0, type0, control1, type1, 'FAIL'))

    # For all mixes    
    for mix in mixes:
        
        # Each controller type
        for control0 in controllers.keys():
            for type0 in controllers[control0]:
                
                # With each other controller type
                for control1 in controllers.keys():
                    try:
                        for type1 in controllers[control1]:
                            handle(mix, control0, type0, control1, type1)
                    except StopIteration:
                        pass
                        
    __dump_warns()
          

def t_test_response_statistics():
    
    mixes = ['MIX0', 'MIX1', 'MIX2', 'MIX0M', 'MIX1M', 'MIX2M']
    controllers = {
                  'Round Robin' : ['Default'],
                  'Optimization' : ['Underbooking', 'Overbooking', 'Default'],
                  'Reactive' : ['Default'],
                  'Proactive' : ['Default']
                  }
    
    rows = []
    ops = ['']
    runs = [0, 1, 2]
    
    def handle(run, mix, control0, type0, control1, type1):
        file0 = '%s_%s_%s_%i' % (control0, mix, type0, run)
        file1 = '%s_%s_%s_%i' % (control1, mix, type1, run)
        
        if file0 == file1:
            raise StopIteration()
        
        try:
            set0 = __load_response_times(file0)
            set1 = __load_response_times(file1)
        except:
            row = [file0 + ' x ' + file1]
            __warn('Skipping error %s' % (row))
            raise StopIteration()
        
        if len(set0) != len(set1):
            row = [file0 + ' x ' + file1]
            __warn('Skipping invalid length %s' % (row))
            raise StopIteration()
        
        # t-test for all operations
        ts = []
        ops = ['Mix', 'Control', 'Type', 'Control', 'Type', 'Name']
        line_found = False
        
        for i in xrange(len(set0)):
            line0 = set0[i]
            line1 = set1[i]
            
            if line0[0] != line1[0]:
                print 'skip line number' 
                break
            
            # Samples
            n1 = float(line0[1])
            n2 = float(line1[1])
            
            # Sample mean
            m1 = float(line0[2])
            m2 = float(line1[2])
            
            # Sample stdev
            s1 = float(line0[3])
            s2 = float(line1[3])
            
            # Welch's t-test
            t, test, df = t_test(m1, m2, s1, s2, n1, n2)
            
            if t > test:
                operation = line0[0]
                ops.append(operation)
                ops.append('df')
                ops.append('sig')
                line_found = True
                
                # print 'Significant t(%i) = %0.2f, p>0.05 -- %s: %s x %s' % (df, t, operation, file0, file1)
                ts.append('%0.2f' % t)
                ts.append('%i' % df)
                ts.append('*')
            else:
                operation = line0[0]
                ops.append(operation)
                ops.append('df')
                ops.append('sig')
                line_found = True
                
                # print '!Significant t(%i) = %0.2f, p>0.05 -- %s: %s x %s' % (df, t, operation, file0, file1)
                ts.append('%0.2f' % t)
                ts.append('%i' % df)
                ts.append('')
               
        if line_found: 
            row = [mix, control0, type0, control1, type1, file0 + ' x ' + file1]
            row.extend(ts)
            rows.append(row)
    
    # For all mixes    
    for mix in mixes:
        
        for run in runs:
        
            # Each controller type
            for control0 in controllers.keys():
                for type0 in controllers[control0]:
                    
                    # With each other controller type
                    for control1 in controllers.keys():
                        try:
                            for type1 in controllers[control1]:
                                handle(run, mix, control0, type0, control1, type1)
                        except StopIteration:
                            pass
                            
        with open('C:/temp/result_%i.csv' % run, 'wb') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter='\t')
            spamwriter.writerow(ops)
            spamwriter.writerows(rows)
            
        __dump_warns()
          
def __plot_aggregated_load_with_migrations(cpu_load_from, timeframe):
    fig = plt.figure()
    
    # Plot accumulated CPU load
    ax = fig.add_subplot(111)
    ax.set_ylabel('Accumulated server load')
    ax.set_xlabel('Time hour:minutes')
    ax.plot(cpu_load_from[1], cpu_load_from[0], label='Server Load')
    ax.axvline(timeframe[0], color='r')
    ax.axvline(timeframe[1], color='r')
 
def __extract_errors(timeframe, logs):
    errors = 0
    for log in logs:
        time = log.timestamp
        
        if time > timeframe[0] and time < (timeframe[1] + 60):
            errors += 1
            
    return errors

def __extract_cpu(timeframe, cpu_load):
    readings_before, readings_during = [], []
    
    for i in xrange(len(cpu_load[0])):
        time = cpu_load[1][i]
        load = cpu_load[0][i]
        
        if time > timeframe[0] and time < timeframe[1]:
            readings_during.append(load)
            
        elif time > (timeframe[0] - 60) and time < timeframe[0]:
            readings_before.append(load)
            
    return readings_before, readings_during 
        
def extract_migration_times(connection):
    # List of migration times
    times = []
    
    # List of migration informations
    info = []
    
    def handle(entry):
        # Refine markers
        raw_frame, _ = __refine_markers(connection)
        
        # Fetch migration data and rain data to sync controller time
        successful, failed, actives, triggered, initial = __fetch_migrations(connection, CONTROLLER_NODE, raw_frame)
        _, release, _ = __fetch_start_benchamrk_syncs(connection, CONTROLLER_NODE, raw_frame)
        _, _, _, _, _, _, _, scenario_start0, errordata0 = __fetch_rain_data(connection, 'load0', raw_frame)
        _, _, _, _, _, _, _, scenario_start1, errordata1 = __fetch_rain_data(connection, 'load1', raw_frame)
        
        # Time correction to synchronize time 
        delta = release - scenario_start0

        # Current domain-node allocation
        current_model = initial
        print current_model

        # Iterate over all successful migrations
        for i, end in enumerate(successful):
            # Migration duration
            times.append((end[1]['duration'],))
            
            # Load server (source, target) load during migration
            correction = delta
            node_from = end[1]['from']
            node_to = end[1]['to']
            domain = end[1]['domain']
            timeframe = (float(end[1]['start']) - correction, float(end[1]['end']) - correction)
            fetchframe = (timeframe[0] - 100, timeframe[1] + 100)
            
            # CPU
            cpu_load_from = __fetch_timeseries(connection, node_from, 'psutilcpu', fetchframe)
            cpu_load_to = __fetch_timeseries(connection, node_to, 'psutilcpu', fetchframe)
            cpu_load_domain = __fetch_timeseries(connection, domain, 'psutilcpu', fetchframe)
            
            # NET
            net_load_from = __fetch_timeseries(connection, node_from, 'psutilnet.br0.sent', fetchframe)
            net_load_to = __fetch_timeseries(connection, node_to, 'psutilnet.br0.recv', fetchframe)
            
            # Update current model and fetch domain loads
            domain_loads_source = []
            domain_loads_target = []
            if current_model != None:
                src_domains = current_model[node_from]
                trg_domains = current_model[node_to] 
                
                # Fetch CPU load of domains
                for domload in src_domains: 
                    cpu_load_domain_i = __fetch_timeseries(connection, domload, 'psutilcpu', fetchframe)
                    domain_loads_source.append(cpu_load_domain_i)
                
                for domload in trg_domains:
                    cpu_load_domain_i = __fetch_timeseries(connection, domload, 'psutilcpu', fetchframe)
                    domain_loads_target.append(cpu_load_domain_i)
                
                # Updated model with migration
                index = [j for j, x in enumerate(src_domains) if x == domain]
                del current_model[node_from][index[0]]
                current_model[node_to].append(domain)
            
            # Plot accumulated server load with migrations
            # __plot_aggregated_load_with_migrations(cpu_load_from, timeframe)

            # CPU load
            before_cpu_source, during_cpu_source = __extract_cpu(timeframe, cpu_load_from)
            before_cpu_target, during_cpu_target = __extract_cpu(timeframe, cpu_load_to)
            before_cpu_domain, during_cpu_domain = __extract_cpu(timeframe, cpu_load_domain)
            
            # NET load
            before_net_source, during_net_source = __extract_cpu(timeframe, net_load_from)
            before_net_target, during_net_target = __extract_cpu(timeframe, net_load_to)
            
            # Sum of domain loads (filter out to get hypervisor load only)
            sum_cpu_source_domains_before, sum_cpu_source_domains_during = 0, 0
            for dom_load in domain_loads_source:
                before, during = __extract_cpu(timeframe, dom_load)
                sum_cpu_source_domains_before += np.sum(before)
                sum_cpu_source_domains_during += np.sum(during)
            
            sum_cpu_target_domains_before, sum_cpu_target_domains_during = 0, 0
            for dom_load in domain_loads_target:
                before, during = __extract_cpu(timeframe, dom_load)
                sum_cpu_target_domains_before += np.sum(before)
                sum_cpu_target_domains_during += np.sum(during)
                        
            # Count errors that were caused by the migration
            errors = __extract_errors(timeframe, errordata0)
            errors += __extract_errors(timeframe, errordata1)
            
            try:
                def agg(values):
                    return np.mean(values)
                
                def agg_h(values, delta):
                    return (np.sum(values) - delta / 2) / len(values)
                
                # Create new result entry
                result = (agg_h(before_cpu_source, sum_cpu_source_domains_before), agg_h(during_cpu_source, sum_cpu_source_domains_during),
                     agg_h(before_cpu_target, sum_cpu_target_domains_before), agg_h(during_cpu_target, sum_cpu_target_domains_during),
                     
                     agg(before_net_source), agg(during_net_source),
                     agg(before_net_target), agg(during_net_target),
                     
                     agg(before_cpu_domain), agg(during_cpu_domain),
                     errors, float(end[1]['duration']))
                
                # Append result entry to list
                info.append(result) 
            except:
                __warn('Error extracting migration infos')
                print 'Error: Could not extract migration infos'
                print before_cpu_source
                print during_cpu_source
                print before_cpu_target
                print during_cpu_target
                print before_net_source
                print during_net_source
                print before_cpu_domain
                print during_cpu_domain
                pass 
            
            
    # Extract migrations for all experiments
    __process_from_experiment_schedule(handle)

    # Write migration times to CSV file 
    with open(configuration.path('migration-times', 'csv'), 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter='\t')
        spamwriter.writerow(('duration',))
        spamwriter.writerows(times)
        
    # Write migration data to CSV file
    with open(configuration.path('migration-data', 'csv'), 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter='\t')
        spamwriter.writerow(('source-before', 'source-during', 'target-before', 'target-during', 'source-net-before',
                             'source-net-during', 'target-net-before', 'target-net-during',
                             'domain-cpu-before', 'domain-cpu-during',
                             'errors', 'duration'))
        spamwriter.writerows(info)


def extract_response_times(connection):
    def handler(entry):
        try:
            # Refine markers
            raw_frame, _ = __refine_markers(connection)
            
            # Load Rain results
            rain_results = __load_rain_results(connection, raw_frame)
            _schedules, _track_configs, _global_metrics, _rain_metrics, _track_metrics, _spec_metrics, _errors = rain_results
            
            # Refine data frame
            data_frame = __refine_data_frame(_schedules)
                
            # Load workload maps
            _, domain_track_map, _ = __domain_workload_map(_track_configs)
            
            print '## RESPONSE TIME EXTRACTION ###'
            # Buffer for all response times 
            agg_resp_time = []
            
            # Fetch track response time and calculate average
            for key in domain_track_map.keys():
                # For all tracks
                for track in domain_track_map[key]:
                    # Load and buffer response response time readings
                    res_resp, _ = __fetch_timeseries(connection, track[0], 'rain.rtime.%s' % track[1], data_frame)
                    agg_resp_time.extend(res_resp)
                    
            print 'Average response time: %i, samples: %i' % (np.mean(agg_resp_time), len(agg_resp_time))
               
            # Write response times to CSV file
            with open(configuration.path('rtime_%s_%s_%s_%i' % (entry[1:]), 'csv'), 'wb') as csvfile:
                spamwriter = csv.writer(csvfile, delimiter='\t') 
                spamwriter.writerows((time,) for time in agg_resp_time)
                
        except:
            print 'Error while processing %s' % entry[1] 
    
    __process_from_experiment_schedule(handler)

     
'''
Calls the callback handler for each experiment registered
in the experiment database. 
'''
def __process_from_experiment_schedule(callback_handler, limit=300):
    # Load experiments database
    count = 0
    for entry in __load_experiment_db(EXPERIMENT_DB):
        print entry
        global START, END, RAW
        RAW = entry[0]
        START, END = RAW.split('    ')
    
        # Upate limit counter
        if count > limit:
            break
        count += 1
    
        # Dump the configuration
        __dump_configuration()
        
        callback_handler(entry)
        
    
'''
Creates a CSV file for the regression analysis
'''
def extract_regression_data(connection):
    header = ['Controller', 'Mix', 'Servers', 'RTime', 'MaxRTime', 'Migrations', 'SrvLoad', 'MemLoad', 'FailOP', 'Violations']
    rows = []
    def handler(entry):
        controller = entry[1]
        mix = entry[2]
        
        data = entry[5]
        servers = float(data[0].replace(',', ''))
        rtime = float(data[5].replace(',', ''))
        maxrtime = float(data[6].replace(',', ''))
        migrations = float(data[10].replace(',', ''))
        srvload = float(data[1].replace(',', ''))
        memload = float(data[2].replace(',', ''))
        failop = float(data[4].replace(',', ''))
        violations = float(data[9].replace(',', ''))
        
        row = [controller, mix, servers, rtime, maxrtime, migrations, srvload, memload, failop, violations]
        rows.append(row)
                    
    # For all experiments
    __process_from_experiment_schedule(handler)
    
    with open(configuration.path('regression', 'csv'), 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter='\t')
        spamwriter.writerow(header)
        spamwriter.writerows(rows)
        
'''
Creates a CSV file for each experiment. It contains the Rain operation response time
metrics for all drivers. 
'''
def extract_response_statistics(connection):
    
    def handler(entry):
        # Refine markers
        raw_frame, _ = __refine_markers(connection)
        
        # Read Rain results
        rain_results = __load_rain_results(connection, raw_frame)
        _schedules, _track_configs, _global_metrics, _rain_metrics, _track_metrics, _spec_metrics, _errors = rain_results
        
        with open(configuration.path('%s_%s_%s_%i' % (entry[1:5]), 'csv'), 'wb') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter='\t')
            print '### Operation Sampling Table ###'
            if len(_global_metrics) < 2:
                print 'error only one global metric found' 
                pass
            
            for global_metric in _global_metrics:
                op = global_metric['operational']['operations']
                for o in op:
                    spamwriter.writerow((o['operation_name'], o['samples_seen'], o['sample_mean'], o['sample_stdev']))
                    print '%s \t %i \t %d \t %d' % (o['operation_name'], o['samples_seen'], o['sample_mean'], o['sample_stdev'])
                    
    # For all experiments
    __process_from_experiment_schedule(handler)


def __refine_markers(connection):
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
    
    return raw_frame, sync_markers
  
def __load_rain_results(connection, raw_frame):
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
        schedule, track_config, global_metrics, rain_metrics, track_metrics, spec_metrics, errors, _, _ = rain_data
        
        if schedule is not None: _schedules.append(schedule)
        if track_config is not None: _track_configs.append((track_config, host))
        if global_metrics is not None: _global_metrics.append(global_metrics)
        if rain_metrics is not None: _rain_metrics.extend(rain_metrics)
        if track_metrics is not None: _track_metrics.extend(track_metrics)
        if spec_metrics is not None: _spec_metrics.extend(spec_metrics)
        if errors is not None: _errors.extend(errors)
        
    # Consistency checks
    if len(_global_metrics) < DRIVERS:
        __warn('Not each driver logged a global metric. Usually one driver exited with an error in this case')
        
    return _schedules, _track_configs, _global_metrics, _rain_metrics, _track_metrics, _spec_metrics, _errors


def __refine_data_frame(rain_schedules):
    # Each rain driver logs an execution schedule which defines the timestamp to start the
    # steady state phase and to end it
    schedule_starts = []
    schedule_ends = []
    for schedule in rain_schedules:
        schedule_starts.append(schedule[0])
        schedule_ends.append(schedule[1])
        __dump_elements(schedule)
       
    # refine data raw_frame with schedules
    data_frame = (max(schedule_starts) / 1000, min(schedule_ends) / 1000)
    __dump_elements(data_frame)
    duration = float(data_frame[1] - data_frame[0]) / 60.0 / 60.0
    print 'Frame duration is: %f hours' % (duration)
    
    return data_frame
    
def __domain_workload_map(rain_track_configs):
    # Results
    domains = []
    domain_track_map = {}
    domain_workload_map = {}
    
    for track_config, source_host in rain_track_configs:
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
                    
    return domains, domain_track_map, domain_workload_map


def __sla_failes(data_frame, domain_track_map):
    sla_fail_count = 0
    for key in domain_track_map.keys():
        for track in domain_track_map[key]:
            res_resp, _ = __fetch_timeseries(connection, track[0], 'rain.rtime.%s' % track[1], data_frame)
            # 3 Second response time "User Preferences and Search Engine Latency" by Jake D. et al.
            # Response Threshold Failures  
            cond = res_resp > 3000 
            ext = np.extract(cond, res_resp)
            sla_fail_count += len(ext)
    return sla_fail_count

def __load_traces(data_frame, domains):
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
        
    return cpu, mem
    

def connect_sonar(connection):
    # Refine markers
    raw_frame, sync_markers = __refine_markers(connection)
    
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
    rain_results = __load_rain_results(connection, raw_frame)
    _schedules, _track_configs, _global_metrics, _rain_metrics, _track_metrics, _spec_metrics, _errors = rain_results 
        
    # Print metrics
    __dump_metrics(_global_metrics, _rain_metrics, _track_metrics, _spec_metrics)
        
    print '## ERRORS ##'
    for error in _errors:
        if error == 'Audit failed: Incorrect value for steadyState, should be 3600':
            pass
        elif error.find('Oops: Uncaught exception caused thread:') != -1:
            print 'critical> ', error
            __warn(error)
        else:
            if len(error) < 100: print error
            else: print error[0:100]
        
    print '## REFINED TIME FRAME ##'
    # refine data raw_frame with schedules
    data_frame = __refine_data_frame(_schedules)
    
    print '## DOMAIN WORKLOAD MAPS (TRACK CONFIGURATION) ##'
    domains, domain_track_map, domain_workload_map = __domain_workload_map(_track_configs) 

    print '## RESPONSE TIME THRESHOLD CHECK ###'
    # Fetch track response time and calculate average
    sla_fail_count = __sla_failes(data_frame, domain_track_map)
    print 'SLA fail count: %i' % sla_fail_count
    
    #####################################################################################################################################
    ### Reading Migrations ##############################################################################################################
    #####################################################################################################################################
    migrations = __fetch_migrations(connection, CONTROLLER_NODE, data_frame)
    migrations_successful, migrations_failed, server_active_flags, migrations_triggered, _ = migrations
    print '## MIGRATIONS ##'
    print 'Successful: %i' % len(migrations_successful)
    print 'Failed: %i' % len(migrations_failed)
    
    #####################################################################################################################################
    ### Resource Readings ###############################################################################################################
    #####################################################################################################################################
    cpu, mem = __load_traces(data_frame, domains)
      
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
    avg_cpu, avg_mem, violations = __analytics_server_utilization(cpu, mem)
    min_nodes, max_nodes = '', ''
    
    print '## MIGRATIONS ##'
    if migrations_successful: 
        servers, avg_cpu, avg_mem, min_nodes, max_nodes = __analytics_migrations(data_frame, cpu, mem, migrations_successful, server_active_flags)
        # __plot_migrations(cpu, mem, migrations_triggered, migrations_successful)
        # __plot_load_vs_servers(data_frame, cpu, mem, server_active_flags, domains)
        # __plot_migrations_vs_resp_time(data_frame, domain_track_map, migrations_triggered, migrations_successful)
        # __analytics_migration_overheads(data_frame, cpu, migrations_successful)
    else:
        print 'No migrations'
    
    print '## GLOBAL METRIC AGGREGATION ###'
    __analytics_global_aggregation(_global_metrics, servers, avg_cpu, avg_mem,
                                   sla_fail_count, len(migrations_successful), min_nodes, max_nodes, violations)
    

if __name__ == '__main__':
    # Dump the configuration
    __dump_configuration()
    
    connection = __connect()
    try:
        connect_sonar(connection)
        # extract_migration_times(connection)
        # extract_regression_data(connection)
        # extract_response_statistics(connection)
        # t_test_response_statistics()
        # t_test_response_statistics_all()
        # extract_response_times(connection)
    except:
        traceback.print_exc(file=sys.stdout)
    __disconnect()
    
    # Dump all warnings that occured
    __dump_warns()
