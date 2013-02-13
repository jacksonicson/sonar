import matplotlib.pyplot as plt
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

def new_plot(ts, threshold=1):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.axis([0.0, len(ts), 0, threshold])
    ax.plot(range(0, len(ts)), ts)
    return fig, ax

def add_plot(fig, ax, ts):
    ax.plot(range(0, len(ts)), ts)
    
def write_plot(filename=None):
    if filename is not None: 
        try:
            plt.savefig('C:/temp/convolution/' + filename)
        except:
            pass

def plot(ts, filename=None, threshold=1):
    '''
    Keyword arguments:
    ts -- numpy array with the time series to plot
    filename -- where to save the plot image to (default=None no plotting)
    threshold -- set a limit on the y axis (default=1 for 100% CPU utilization)
    '''
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.axis([0.0, len(ts), 0, threshold])
    ax.plot(range(0, len(ts)), ts)
    
    if filename is not None: 
        try:
            plt.savefig('C:/temp/convolution/' + filename)
        except:
            pass
