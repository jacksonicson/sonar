import numpy as np

def to_array(timeSeries):
    time = np.empty(len(timeSeries.elements))
    demand = np.empty(len(timeSeries.elements))
    
    for i in range(0, len(timeSeries.elements)):
        time[i] = timeSeries.elements[i].timestamp
        demand[i] = timeSeries.elements[i].value
        
    return time, demand

def to_array_collector(timeSeries):
    time = np.empty(len(timeSeries))
    demand = np.empty(len(timeSeries))
    
    for i in range(0, len(timeSeries)):
        time[i] = timeSeries[i].timestamp
        demand[i] = timeSeries[i].value
        
    return time, demand