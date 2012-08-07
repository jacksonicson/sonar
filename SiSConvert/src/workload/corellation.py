import numpy as np
from service import times_client
import matplotlib.pyplot as plt
from scipy import signal
import scipy as sp

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
    
    print len(load)
    
    #load = load - mean
    
    
    # http://www.simafore.com/blog/bid/105815/Time-series-analysis-using-R-for-cost-forecasting-models-in-8-steps
    
    
    # load = np.array([np.sin(i) for i in range(0,500)])
    
    # load = np.log10(load)    
    # result = np.correlate(load, load, 'full')
    # result = result[0:len(result)]
    
    from scipy import signal
    # load = sp.signal.detrend(load, axis=0)
    
    t = np.arange(len(load))
    sp = np.fft.fft(load)
    freq = np.fft.fftfreq(t.shape[-1])
    
    from pandas.tools.plotting import autocorrelation_plot
    autocorrelation_plot(load)
        
    fig = plt.figure()
    ax = fig.add_subplot(111)
    # ax.plot(range(0, len(ff)), ff)
    ax.plot(freq, sp.real, freq, sp.imag)
    # ax.acorr(load, maxlags=700)
    
    
    
    
    print 'pandas'    
    from pandas import Series
    s = Series(load, index=range(0, len(load)))
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
