import numpy as np

def to_array(timeSeries):
    time = np.empty(len(timeSeries.elements))
    demand = np.empty(len(timeSeries.elements))
    
    for i in range(0, len(timeSeries.elements)):
        time[i] = timeSeries.elements[i].timestamp
        demand[i] = timeSeries.elements[i].value
        
    return time, demand

def to_array_collector(timeSeries, timeframe):
    time = np.empty(len(timeSeries))
    demand = np.empty(len(timeSeries))
        
    iout = 0
    for i in xrange(0, len(timeSeries)):
        test = timeSeries[i].timestamp
        if test < timeframe[0] or test > timeframe[1]:
            continue
        
        time[iout] = timeSeries[i].timestamp
        demand[iout] = timeSeries[i].value
        iout += 1
        
    time = time[0:iout]
    demand = demand[0:iout]
        
    return time, demand