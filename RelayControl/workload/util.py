import numpy as np

def to_array(timeSeries):
    time = np.zeros(len(timeSeries.elements))
    demand = np.zeros(len(timeSeries.elements))
    for i in range(0, len(timeSeries.elements)):
        time[i] = timeSeries.elements[i].timestamp
        demand[i] = timeSeries.elements[i].value
        
    return time, demand