from scipy import *
from scipy.signal import *
from service import times_client
import array
import csv
import math
import matplotlib.pyplot as plt
import numpy as np
import os
import random
import scipy
import scipy.stats as stats
import signal

def gaussian_smooth(list, degree=5):  
    window = degree * 2 - 1  
    weight = np.array([1.0] * window)  
    weightGauss = [] 
    for i in range(window):  
        i = i - degree + 1  
        frac = i / float(window)  
        gauss = 1 / (np.exp((4 * (frac)) ** 2))  
        weightGauss.append(gauss)  
    weight = np.array(weightGauss) * weight  
    smoothed = [0.0] * (len(list) - window)  
    for i in range(len(smoothed)):  
        smoothed[i] = sum(np.array(list[i:i + window]) * weight) / sum(weight)  
    return smoothed  
 
 
def create_ibis_convolution(signal, buckets, period_width):
    # Create a set for each bucket
    convolution = [[] for x in xrange(buckets)]
     
    # Bucket with (number of samples per bucket)
    bucket_width = period_width / buckets
    
    # Iterate over each period (day, week, ...)
    for period_signal_index in range(0, len(signal), period_width):
        
        # Iterate over all buckets within the period 
        for bucket_index in range(0, buckets):
            
            # Calculate the sampling offset for this bucket
            bucket_signal_start = period_signal_index + bucket_index * bucket_width
            
            # Calculate the sampling end for this bucket
            bucket_signal_end = min(bucket_width, len(signal) - bucket_signal_start)
            
            # Add everything between this offsets to the bucket
            for signal_index in range(bucket_signal_start, bucket_signal_start + bucket_signal_end):
                value = signal[signal_index]
                convolution[bucket_index].append(value) 
            
    # Return the buckets (convolution)
    return convolution


def convoluation_average(convolution):
    signal_out = []
    
    for bucket in convolution: 
        b = np.array(bucket)
        value = mean(b)
        signal_out.append(value)
    
    return signal_out


def convoluation_percentile(convolution, percentile=50):
    signal_out = []
    
    for bucket in convolution: 
        b = np.array(bucket)
        value = stats.scoreatpercentile(b, percentile)
        signal_out.append(value)
    
    return signal_out


def signal_gauss_smooth(signal, width=4):
    filt = gaussian(width, 4)
    filt /= sum(filt)
    n = len(signal)
    padded = concatenate((signal[0] * ones(width // 2), signal, signal[n - 1] * ones(width // 2)))
    result = convolve(padded, filt, mode='valid')
    return result


def add_noise(signal, convolution, bucket_signal_width=1, lower_percentile=5, upper_percentile=95):
    for i, bucket in enumerate(convolution):
        array_bucket = np.array(bucket)
        lower_bound = stats.scoreatpercentile(array_bucket, lower_percentile)
        upper_bound = stats.scoreatpercentile(array_bucket, upper_percentile)
        
        # Calculate the stdv
        filtered_values = []
        for value in bucket:
            if value >= lower_bound and value <= upper_bound:
                filtered_values.append(value)
                
        array_filtered_bucket = np.array(filtered_values)
        std_dev = (scipy.std(array_filtered_bucket) / 2.0) + 0.0000001
                
        min_range = min(bucket_signal_width, len(signal) - i)
        index = i * bucket_signal_width
        noise_value = np.random.normal(0, std_dev, min_range)
        for j in range(index, index + min_range):
            signal[j] += noise_value[j - index]

    return signal


def increase_resolution(signal, bucket_signal_width=1):
    res_signal = []
    
    for value in signal:
        for i in range(0, bucket_signal_width):
            res_signal.append(value)
            
    return res_signal


def extract_signal(elements):
    signal = []
    
    for element in elements:
        signal.append(element.value)
        
    return signal



def normalize_signal(signal, nv=1.0, percentile=95):
    normalized_signal = []
    signal_max = scipy.stats.scoreatpercentile(signal, percentile)

    for value in signal: 
        normalized = value / signal_max * nv
        normalized = min(nv, normalized)
        normalized_signal.append(normalized)
    
    return signal # normalized_signal


def filter_extremes(bucket, lower_percentile=5, upper_percentile=95):
    array_bucket = np.array(bucket)
    lower_bound = stats.scoreatpercentile(array_bucket, lower_percentile)
    upper_bound = stats.scoreatpercentile(array_bucket, upper_percentile)
    
    result = []
    for element in bucket: 
        if element > lower_bound and element < upper_bound: 
            result.append(element) 
    
    return result


def plot_bucket_histogram(bucket):
    fig = plt.figure()
    
    ax = fig.add_subplot(111)
    
    plt.xlabel('Time')
    plt.ylabel('Service Demand')

    ax.hist(bucket, 15)
    
    plt.show()    
    
    
def plot_convolution(ax, convolution, bucket_width):
    plt.xlabel('Time')
    plt.ylabel('Service Demand')
    
    points = []
    indices = []
    
    index = 0
    for bucket in convolution: 
        points += bucket
        indices += [index] * len(bucket)
        index += bucket_width
    
    ax.scatter(indices, points, marker='x', s=1)


def plot_signal(ax, signal):
    index = range(0, len(signal))
    ax.plot(index, signal)


def print_overhead(signal):
    for element in signal: 
        value = element * 0.4
        print value


def process_file(filename, elements, periodicity, frequency, smoothening_factor):
    """
    periodicty: defines the periodicity of the signal in seconds
    frequency: defines the frequency samples are taken (s/1)
    
    smoothening_factor: factor used for smoothening the raw signal
    buckets: number of buckets used
    
    returns: the frequency of the profile signal
    """
    
    periodicity_samples = int(periodicity / frequency)
    # upper an lower percentile for the white noise
    UPPER_PERCENTILE = 80 
    LOWER_PERCENTILE = 20
    
    # number of buckets to create per convolution
    BUCKETS = 24
    
    # number of samples per bucket (upscaling)
    SCALE = 12 
    
    # Signal processing    
    raw_signal = extract_signal(elements)

    # Normalize the signal to 1
    raw_signal = normalize_signal(raw_signal)
    
    # Execute the convolution
    convolution = create_ibis_convolution(raw_signal, BUCKETS, periodicity_samples)
    
    # upper and lower percentiles
    signal_upper = convoluation_percentile(convolution, UPPER_PERCENTILE)
    signal_lower = convoluation_percentile(convolution, LOWER_PERCENTILE)
    
    # Signal of the average values of each buckets of the convolution
    signal = convoluation_average(convolution)
    signal2 = signal
#    
#    signal_orig = signal
#    signal_orig = normalize_signal(signal_orig)
#    print_overhead(signal_orig)
    
    # Increase resolution of the signal (creates a rectangular signal with 
    # each rectangle has the width of SCALE)
    signal = increase_resolution(signal, SCALE)
    
    # Increase resolution of the upper and lower bound signals as well
    signal_upper = increase_resolution(signal_upper, SCALE)
    signal_lower = increase_resolution(signal_lower, SCALE)
    
    # Execute a smoothening on the signal
    signal = signal_gauss_smooth(signal, smoothening_factor)
    
    # Finally add noise using the upper and lower bound signals
    signal = add_noise(signal, convolution, SCALE, LOWER_PERCENTILE, UPPER_PERCENTILE)
    
    # Calculate the frequency of the output signal
    output_signal_frequency_a = float(periodicity) / float(len(signal))
    output_signal_frequency = float(periodicity) / float(BUCKETS * SCALE)
    
    print "output signal frequency %d, %d" % (output_signal_frequency_a, output_signal_frequency)
    
    # Save signal to database
    #from timeseries import timeserie
    #timeserie.write_list(signal_orig, '/tmp' + filename, output_signal_frequency)
    
    # #####################################################
    # Plot signals 
    fig = plt.figure(num=None, figsize=(8, 5), dpi=95)
    ax = fig.add_subplot(111)
    plt.xlabel('Time')
    plt.ylabel('Service Demand')
    ax.set_title(filename);
    
    #plot_convolution(ax, convolution, SCALE)
    #plot_signal(ax, signal_upper)
    #plot_signal(ax, signal_lower)
    plot_signal(ax, signal)
    # plot_signal(ax, signal_orig)
    
    fname = filename + '.png'
    fname = fname.replace('/', '_')
    # fig.savefig('../../target/%s' % (fname))
    
    # Show the plot in a window
    # plt.show()
    
    plt.savefig('C:/temp/convolution/' + filename + '.png', papertype='a4')
    
    return signal
    

def load_trace(filename):
    fs = gridfs.GridFS(storage.db, collection='tracefiles')
    
    # Check if this file exists already
    if fs.exists(filename=filename) == False:
        return 
    
    gfile = fs.get_last_version(filename=filename)
    
    trace = trace_pb2.Trace()
    trace.ParseFromString(gfile.read())
    return trace


def process_trace(name):
    print 'Downloading...'
    connection = times_client.connect()
    timeSeries = connection.load(name)
    times_client.close()
    print 'complete'
    
    # 24 hours
    periodicity = 24.0 * 3600.0 # day
    frequency = 3600 # hour
    smoothening = 30
    return process_file(name, timeSeries.elements, periodicity, frequency, smoothening)


def plot_overlay(plots):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.xlabel('Time')
    plt.ylabel('Service Demand')
    ax.set_title('Signal Overlay');
    
    accumulated_signal = None
    
    for plot in plots:
        trace = load_trace(plot)
        
        signal = []
        for element in trace.elements:
            signal.append(element.value) 
        
        if accumulated_signal == None: 
            accumulated_signal = signal
        else:
            for i in range(0, len(signal)):
                accumulated_signal[i] += signal[i]          
         
        plot_signal(ax, signal)
        
        
    plot_signal(ax, accumulated_signal)
    
    # Save
    fname = 'aggregated' + '.png'
    fname = fname.replace('/', '_')
    #fig.savefig('../../target/%s' % (fname))
    
    # Show the plot in a window
    plt.show()    
    
def gen_html(result):
    import StringIO
    pages = []
    count = 0
    while count < len(result):
        buffer = StringIO.StringIO()
        pages.append(buffer)
        
        buffer.write("<html><body>")
    
        to = count + 20
        for i in range(count, to):
            if i >= len(result):
                break
            r = result[i]
            print i
            buffer.write('<a href="' + r + '.png"><img src="' + r + '.png" width="200" height="150"></img></a>')
        print "next"
        
        count += 20
        
    count = 1
    pcount = 0
    for buffer in pages:  
        buffer.write('<a href="index' + str(count) + '.html">next</a>')
        count += 1
                  
        buffer.write("</body></html>")
        value = buffer.getvalue()
        buffer.close()
        
        f = open('C:/temp/convolution/index' + str(pcount) + '.html', 'w')
        pcount += 1
        f.write(value)
        f.close()
    
if __name__ == '__main__':
    connection = times_client.connect()
    
    result = [] # connection.find('^O2_.*\Z')
    result.extend(connection.find('^SIS_133_cpu.*\Z'))
    
    times_client.close()
    
    if True:
        for r in result: 
            print r
            try:
                process_trace(r)
            except Exception, e :
                print 'error in processing %s' % (r)
    