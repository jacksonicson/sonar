import numpy as np
from service import times_client
import matplotlib.pyplot as plt
from scipy import signal

def process_trace(connection, name):
    print 'Downloading...'
    timeSeries = connection.load(name)
    print 'complete'

    time = np.zeros(len(timeSeries.elements))
    load = np.zeros(len(timeSeries.elements))
    for i in range(0, len(timeSeries.elements)):
        time[i] = timeSeries.elements[i].timestamp
        load[i] = timeSeries.elements[i].value
        
    
    mean = np.mean(load)
    load = load - mean
    # load = np.log10(load)    
    result = np.correlate(load, load, 'full')
    
    
    import statsmodels.api as sm
    
    
    z = sm.nonparametric.lowess(np.array(range(0, len(load))),load, frac= 1./3, it=0)
    
    #load = z[:,0:1]
    #load = np.ravel(load)
    #print load
        
    fig = plt.figure()
    ax = fig.add_subplot(111)
    # ax.plot(range(0, len(result)), result)
    # ax.acorr( load,usevlines=True,maxlags=None,normed=True,lw=2)
    
#    fig = plt.figure()
#    ax = fig.add_subplot(111)
    ax.plot(range(0, len(result)), result)
    
    plt.show()
    

if __name__ == '__main__':
    connection = times_client.connect()
    result = connection.find('^O2_business_UPDATEACCOUNT\Z')
    
    for r in result: 
        print r
        process_trace(connection, r)
    
    times_client.close()
