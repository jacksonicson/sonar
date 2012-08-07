from service import times_client
import matplotlib.pyplot as plt
import numpy as np

def simple_moving_average(array, window=5):
    weights = np.repeat(1.0, window) / window
    return np.convolve(array, weights)[window - 1:-(window - 1)]

def average_bucket(floor_array):
    return np.median(floor_array)

def to_weekday(value):
    day = long(long(value) / (24 * 60 * 60)) % 7
    return day
 
def to_positive(value):
    if value < 0:
        value = 0
    return value
 
def extract_profile(name, time, signal):
    cycle_time = 24 * 60 * 60
    sampling_frequency = 60 * 60 # 15 * 60 # 60 * 60 # O2
     
    elements_per_cycle = cycle_time / sampling_frequency
    cycle_count = len(signal) / elements_per_cycle

    print 'Number of cycles %i' % (cycle_count)
        
    # Remove Weekends/Sundays
    tv = np.vectorize(to_weekday)
    time = tv(time)
    indices = np.where(time < 5)
    time = np.take(time, indices)
    signal = np.ravel(np.take(signal, indices))
    
    # Buffer original signal
    org_signal = signal
        
    # TODO: Filter extreme values > the 95th percentile
    # TODO: Signal normalization
        
    # Remove the remainder elements
    signal = np.resize(signal, (1, cycle_count * elements_per_cycle))

    # Reshape the signal (each cycle in its on row)    
    signal = np.reshape(signal, (-1, elements_per_cycle))
    
    # Get Buckets
    bucket_time = 1 * 60 * 60
    bucket_count = cycle_time / bucket_time
    elements_per_bucket = elements_per_cycle / bucket_count
    
    print 'elements per bucket %i' % (elements_per_bucket)
    
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
        variance_array[i] = var / 20
    variance_array = np.ravel(variance_array)
    
    # Variance calculation two
    variance_array_2 = np.empty((len(buckets), 1), np.float32) # per bucket averaged variance
    for i in range(0, len(buckets)):
        bucket = buckets[i]
        variance = np.apply_along_axis(np.std, 1, bucket)
        variance = np.median(np.ravel(variance))
        variance_array_2[i] = variance / 2
    variance_array_2 = np.ravel(variance_array)
     
    
    # Increase signal resolution
    resolution_factor = 5
    noise_profile = np.ravel(np.array(zip(*[raw_profile for i in range(0, resolution_factor)])))
    
    # Smooth
    noise_profile = simple_moving_average(noise_profile, 15)
    
    # Create noise
    noise_array = np.array(0, np.float32)
    for i in range(0, len(noise_profile), resolution_factor):
        j = i / resolution_factor
        variance = variance_array_2[j]
        if variance > 0:
            noise = np.random.normal(0, variance, resolution_factor)
            noise_array = np.hstack((noise_array, noise))
        else:
            noise = np.array(resolution_factor, np.float32)
            noise_array = np.hstack((noise_array, noise))
    
    noise_profile = np.resize(noise_profile, len(noise_array))
    noise_profile = noise_profile + noise_array
    
    tv = np.vectorize(to_positive)
    noise_profile = tv(noise_profile)

    # Plotting    
    fig = plt.figure()
    fig.suptitle(name)
    ax = fig.add_subplot(311)
    ax.plot(range(0, len(noise_profile)), noise_profile)
    
    ax = fig.add_subplot(312)
    ax.plot(range(0, len(org_signal)), org_signal)
    
    ax = fig.add_subplot(313)
    ax.plot(range(0, len(variance_array_2)), variance_array_2)
    
    
     
def process_trace(connection, name):
    print 'Downloading...'
    timeSeries = connection.load(name)
    print 'complete'

    time = np.zeros(len(timeSeries.elements))
    load = np.zeros(len(timeSeries.elements))
    for i in range(0, len(timeSeries.elements)):
        time[i] = timeSeries.elements[i].timestamp
        load[i] = timeSeries.elements[i].value
        
    
    extract_profile(name, time, load)
    
    # plt.show()
    plt.savefig('C:/temp/convolution/' + name + '.png')

if __name__ == '__main__':
    connection = times_client.connect()
    result = connection.find('^O2_.*\Z')
    
    selected = ['O2_business_UPDATEDSSLINE',    # Burst in the evening
                'O2_business_ADDUCP',           # Day workload
                'O2_business_LINECONFIRM',      # Day nand night workload
                'O2_retail_ADDORDER',           # Night and low day workload
                'O2_retail_PIRANHAREQUEST',     # No shape workload (random spikes) 
                'O2_retail_SENDMSG',            # Day workload flattens till evening
                'O2_retail_PORTORDER',          # Random spikes 
                'O2_retail_UPDATEDSS',          # Night workload
                '', 
                '',
                '', 
                '',
                '', 
                '',
                '', 
                '',
                '', 
                '',
                '', 
                '',
                ]
    
#    for s in selected:
#        result = connection.find(r'^' + s + r'\Z')
    
    for r in result: 
        print r
        process_trace(connection, r)
    
    times_client.close()

