import matplotlib.pyplot as plt
import analytics
from collector import CollectService, ManagementService, ttypes
from datetime import date
import time
import configuration

##########################
## Configuration        ##
##########################
RAW = '29/11/2012 8:45:00    30/11/2012 00:50:00'
##########################

# If RAW exists use this one
START = ''
END = ''
if RAW is not None:
    START, END = RAW.split('    ')

def __to_date(ts):
    return time.gmtime(ts).tm_hour

def __fetch_logs(connection, load_host, sensor_name, timeframe):
    # Build query
    query = ttypes.LogsQuery()
    query.hostname = load_host
    query.sensor = sensor_name
    query.startTime = timeframe[0]
    query.stopTime = timeframe[1]
    logs = connection.queryLogs(query)
    
    timestamps = []
    priority = []
    
    # scan logs for results
    for log in logs:
        if log.timestamp > (timeframe[1] + 5 * 60) * 1000:
            print 'skipping remaining log messages - out of timeframe'
            break
        
        timestamps.append(log.timestamp)
        priority.append(log.logLevel)
        
        
    return timestamps, priority

def main():
    connection = analytics.__connect()
    start = analytics.__to_timestamp(START)
    stop = analytics.__to_timestamp(END)
    raw_frame = (start, stop)
    
    s0_result, s0_time = analytics.__fetch_timeseries(connection, 'srv0', 'psutilcpu', raw_frame)
    
    ts0, pr0 = __fetch_logs(connection, 'Andreas-PC', 'start_benchmark', raw_frame)
    ts1, pr1 = __fetch_logs(connection, 'load0', 'rain', raw_frame)
    
    analytics.__disconnect()
    
    # Setup the new plot
    fig = plt.figure()
    fig.set_size_inches((10, 6))
    plt.xlabel('Time')
    plt.ylabel('Server Load')
    
    # Create a new subplot
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(s0_time, s0_result, linewidth=0.3)
    ax.set_ylim((0, 150))
    ax.set_xticklabels(
        [__to_date(data) for data in ts0]
        )
    
    # Draw lines for messages
    for i, ts in enumerate(ts0):
        if pr0[i] > 5000:
            # ax.axvline(ts, color='m')
            ax.axvline(x=ts, ymin=0.9, ymax=0.95, linewidth=0.3, color='m')
    for i,ts in enumerate(ts1):
        ax.axvline(x=ts, ymin=0.85, ymax=0.9, linewidth=0.3, color='r')

    # Display the plot
    plt.savefig(configuration.path('sonar_concept', 'pdf'))        
    # plt.show()

if __name__ == '__main__':
    main()