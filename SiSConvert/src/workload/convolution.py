import numpy as np
from service import times_client
import matplotlib.pyplot as plt

def simple_moving_average(array, window=5):
    weights = np.repeat(1.0, window) / window
    return np.convolve(array, weights)[window - 1:-(window - 1)]

def average_bucket(floor_array):
    return np.average(floor_array)

def to_weekday(value):
    day = long(long(value) / (24 * 60 * 60)) % 7
    return day
 
def extract_profile(time, signal):
    # All calculations are in seconds
    # cycle = 24 hours
    # sampling frequency = 15 minutes 
    cycle_time = 24 * 60 * 60
    sampling_frequency = 60 * 60
    elements_per_cycle = cycle_time / sampling_frequency
    cycle_count = len(signal) / elements_per_cycle

    cover_days = (len(signal) * sampling_frequency) / (60 * 60 * 24)
    print 'TS covers %i days' % (cover_days)
        
    # Remove Weekends/Sundays
    tv = np.vectorize(to_weekday)
    time = tv(time)
    
    indices = np.where(time != 6)
    time = np.take(time, indices)
    signal = np.ravel(np.take(signal, indices))
        
    # TODO: Filter extreme values > the 95th percentile
    # TODO: Signal normalization
        
    # Remove the remainder elements
    signal = np.resize(signal, (1, cycle_count * elements_per_cycle))

    # Reshape the signal (each cycle in its on row)    
    signal = np.reshape(signal, (-1, elements_per_cycle))
    
    # Get Buckets
    bucket_time = 1 * 60 * 60
    bucket_count = cycle_time / bucket_time
    
    # Split the signal
    buckets = np.hsplit(signal, bucket_count)
    
    # Reduce buckets
    bucket_array = np.empty((signal.shape[0], 0), np.float32)
    for bucket in buckets:
        bucket = np.apply_along_axis(average_bucket, 1, bucket)
        bucket = np.reshape(bucket, (signal.shape[0], 1))
        bucket_array = np.hstack((bucket_array, bucket))

    # Get averaged bucket
    raw_profile = np.apply_along_axis(average_bucket, 0, bucket_array)
    raw_profile = np.reshape(raw_profile, (raw_profile.shape[0], 1))
    raw_profile = raw_profile[:, 0:1]

    # Variance
    # TODO: Consider only values between the 5th and 95th percentile
    variance_array = np.empty((len(buckets), 1), np.float32)
    for i in range(0, len(buckets)):
        bucket = buckets[i]
        bucket = np.ravel(bucket)
        var = np.std(bucket)
        variance_array[i] = var
    variance_array = np.ravel(variance_array)
    
    # Increase signal resolution
    resolution_factor = 5
    noise_profile = np.ravel(np.array(zip(*[raw_profile for i in range(0, resolution_factor)])))
    
    # Smooth
    noise_profile = simple_moving_average(noise_profile, 15)
    
    # Create noise
    noise_array = np.array(0, np.float32)
    for i in range(0, len(noise_profile), resolution_factor):
        j = i / resolution_factor
        variance = variance_array[j]
        noise = np.random.normal(0, variance / 10.0, resolution_factor)
        noise_array = np.hstack((noise_array, noise))
    
    noise_profile = np.resize(noise_profile, len(noise_array))
    noise_profile = noise_profile + noise_array

    # Plotting    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(range(0, len(noise_profile)), noise_profile)
    
    plt.show()
    
     
def process_trace(connection, name):
    print 'Downloading...'
    timeSeries = connection.load(name)
    print 'complete'

    time = np.zeros(len(timeSeries.elements))
    load = np.zeros(len(timeSeries.elements))
    for i in range(0, len(timeSeries.elements)):
        time[i] = timeSeries.elements[i].timestamp
        load[i] = timeSeries.elements[i].value
        
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(range(0, len(load) * 60, 60), load)
    
    extract_profile(time, load)


if __name__ == '__main__':
    connection = times_client.connect()
    result = connection.find('^O2_business_CONTRACTEXT\Z')
    
    for r in result: 
        print r
        process_trace(connection, r)
    
    times_client.close()

