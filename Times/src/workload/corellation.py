import numpy as np
from service import times_client
import matplotlib.pyplot as plt
from scipy import signal
import scipy as sp

def process_trace(connection, name):
    print 'Downloading...'
    timeSeries = connection.demand(name)
    print 'complete'

    time = np.zeros(len(timeSeries.elements))
    demand = np.zeros(len(timeSeries.elements))
    for i in range(0, len(timeSeries.elements)):
        time[i] = timeSeries.elements[i].timestamp
        demand[i] = timeSeries.elements[i].value
        
    
    mean = np.mean(demand)
    
    print len(demand)
    
    #demand = demand - mean
    
    
    # http://www.simafore.com/blog/bid/105815/Time-series-analysis-using-R-for-cost-forecasting-models-in-8-steps
    
    
    # demand = np.array([np.sin(i) for i in range(0,500)])
    
    # demand = np.log10(demand)    
    # result = np.correlate(demand, demand, 'full')
    # result = result[0:len(result)]
    
    from scipy import signal
    # demand = sp.signal.detrend(demand, axis=0)
    
    t = np.arange(len(demand))
    sp = np.fft.fft(demand)
    freq = np.fft.fftfreq(t.shape[-1])
    
    from pandas.tools.plotting import autocorrelation_plot
    autocorrelation_plot(demand)
        
    fig = plt.figure()
    ax = fig.add_subplot(111)
    # ax.plot(range(0, len(ff)), ff)
    ax.plot(freq, sp.real, freq, sp.imag)
    # ax.acorr(demand, maxlags=700)
    
    
    
    
    print 'pandas'    
    from pandas import Series
    s = Series(demand, index=range(0, len(demand)))
    corr = s.autocorr()
    print corr
    
    plt.show()
   

if __name__ == '__main__':
    connection = times_client.connect()
    result = connection.find('^SIS_194_mem\Z')
    
    for r in result: 
        print r
        process_trace(connection, r)
    
    times_client.close()
