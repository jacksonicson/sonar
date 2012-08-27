from service import times_client
from times import ttypes
import matplotlib.pyplot as plt
import numpy as np


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

 
def extract_profile(name, time, signal, sampling_frequency, cycle_time=24 * 60 * 60, plot=False):
    tv = np.vectorize(to_weekday)
    time = tv(time)
    indices = np.where(time < 5)
    time = np.take(time, indices)
    signal = np.ravel(np.take(signal, indices))
    
    elements_per_cycle = cycle_time / sampling_frequency
    cycle_count = len(signal) / elements_per_cycle
    
    # Buffer original signal
    org_signal = signal
        
    # TODO: Filter extreme values > the 95th percentile
        
    # Remove the remainder elements
    signal = np.resize(signal, cycle_count * elements_per_cycle)

    # Reshape the signal (each cycle in its on row)    
    signal = np.reshape(signal, (-1, elements_per_cycle))
    
    # Get Buckets
    bucket_time = 1 * 60 * 60
    bucket_count = cycle_time / bucket_time
    elements_per_bucket = elements_per_cycle / bucket_count
    
    # Split the signal
    buckets = np.hsplit(signal, bucket_count)
    
    # Reduce buckets
#    bucket_array = np.empty((signal.shape[0], 0), np.float32)
    bucket_array = np.empty(bucket_count, np.float32)
    i = 0
    for bucket in buckets:
#        bucket = np.apply_along_axis(average_bucket, 1, bucket)
#        bucket = np.reshape(bucket, (signal.shape[0], 1))
#        bucket_array = np.hstack((bucket_array, bucket))
        np.reshape(bucket, (signal.shape[0] * elements_per_bucket,1))
        value = np.mean(bucket)
        bucket_array[i] = value
        i += 1

    # Get averaged bucket
#    raw_profile = np.apply_along_axis(average_bucket, 0, bucket_array)
    raw_profile = bucket_array

    # Variance
    # TODO: Consider only values between the 5th and 95th percentile
    variance_array = np.empty(len(buckets), np.float32)
    for i in range(0, len(buckets)):
        bucket = buckets[i]
        bucket = np.ravel(bucket)
        var = np.std(bucket)
        variance_array[i] = var / 30
    variance_array = np.ravel(variance_array)
    
    # Variance calculation two
    variance_array_2 = np.empty(len(buckets), np.float32) # per bucket averaged variance
    for i in range(0, len(buckets)):
        bucket = buckets[i]
        variance = np.apply_along_axis(np.std, 1, bucket)
        variance = np.median(np.ravel(variance))
        variance_array_2[i] = variance / 2
    variance_array_2 = np.ravel(variance_array)
    
    # Increase signal resolution
    target_bucket_count = cycle_time / (5 * 60)
    resolution_factor = target_bucket_count / bucket_count
    noise_profile = np.ravel(np.array(zip(*[raw_profile for _ in xrange(resolution_factor)])))
    
    # Smooth
    smooth_profile = simple_moving_average(noise_profile, 7)
    
    # Create noise
    noise_array = np.array(0, np.float32)
    for i in xrange(0, len(noise_profile), resolution_factor):
        j = i / resolution_factor
        variance = variance_array[j]
        if variance > 0:
            noise = np.random.normal(0, variance, resolution_factor)
            noise_array = np.hstack((noise_array, noise))
        else:
            noise = np.zeros(resolution_factor, np.float32)
            noise_array = np.hstack((noise_array, noise))
    
    # Apply noise
    smooth_profile = smooth_profile + noise_array
    
    # Limit to positive
    tv = np.vectorize(to_positive)
    smooth_profile = tv(smooth_profile)

    # Frequency of result signal
    frequency = cycle_time / len(smooth_profile)
    

    # Plotting
    if plot: _plot(name, smooth_profile, org_signal, variance_array_2)   
        
        
    return smooth_profile, frequency
    

def _plot(name, smooth_profile, org_signal, variance_array_2):
    fig = plt.figure()
    fig.suptitle(name)
    ax = fig.add_subplot(311)
    ax.plot(range(0, len(smooth_profile)), smooth_profile)
    
    ax = fig.add_subplot(312)
    ax.plot(range(0, len(org_signal)), org_signal)
    
    ax = fig.add_subplot(313)
    ax.plot(range(0, len(variance_array_2)), variance_array_2)

    try:    
        plt.savefig('C:/temp/convolution/' + name + '.png')
    except:
        print 'Warning, could not save plot %s' % (name)
    
    
def process_trace(connection, name, sample_frequency, cycle_time):
    # Download Times TS elements
    timeSeries = connection.load(name)

    # Create a data and time array from the Times TS elements
    time = np.zeros(len(timeSeries.elements))
    data = np.zeros(len(timeSeries.elements))
    for i in range(0, len(timeSeries.elements)):
        time[i] = timeSeries.elements[i].timestamp
        data[i] = timeSeries.elements[i].value
        
    # Extract profile from the array
    return extract_profile(name, time, data, sample_frequency, cycle_time)

