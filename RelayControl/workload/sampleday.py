import matplotlib.pyplot as plt
import numpy as np
import util

def simple_moving_average(array, window=5):
    weights = np.repeat(1.0, window) / window
    return np.convolve(array, weights)[0:-5]

def average_bucket(floor_array):
    return np.mean(floor_array)

def to_weekday(value):
    day = long(long(value) / (24 * 60 * 60)) % 7
    return day
 
def to_positive(value):
    if value < 0:
        value = 0
    return value
 
def sample_day(name, time, signal, sampling_frequency, cycle_time=24 * 60 * 60, day=8, plot=False):
    # Remove Weekends/Sundays
    tv = np.vectorize(to_weekday)
    time = tv(time)
    indices = np.where(time < 5)
    time = np.take(time, indices)
    signal = np.ravel(np.take(signal, indices))
    
    elements_per_cycle = cycle_time / sampling_frequency
    cycle_count = len(signal) / elements_per_cycle
    
    # Remove the remainder elements
    signal = np.resize(signal, cycle_count * elements_per_cycle)

    # Get 95%tile
    pcntile = np.percentile(signal, 99)
    mean = np.mean(signal)
    indices = np.where(signal > pcntile)
    signal[indices] = mean

    # Reshape the signal (each cycle in its on row)    
    signal = np.reshape(signal, (-1, elements_per_cycle))
    
    # Extract day 
    day_signal = signal[day]
    
    # Get Buckets
    bucket_count = cycle_time / (5 * 60)
    assert bucket_count == np.shape(day_signal)[0]

    smooth_profile = simple_moving_average(day_signal, 7)
    
    frequency = cycle_time / len(smooth_profile)
    
    # Plotting
    if plot:    
        fig = plt.figure()
        fig.suptitle(name)
        ax = fig.add_subplot(111)
        ax.plot(signal[1, ])
    
        try:    
            plt.savefig('C:/temp/convolution/' + name + '_sampleday.png')
        except:
            print 'Warning, could not save plot %s' % (name)
        
    return smooth_profile, frequency
    
def process_trace(connection, name, ifreq, cycle_time, day):
    timeSeries = connection.load(name)
    time,demand = util.to_array(timeSeries)        
    return sample_day(name, time, demand, ifreq, cycle_time, day=day)

