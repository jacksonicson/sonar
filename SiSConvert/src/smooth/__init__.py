from configuration import storage
from proto import trace_pb2
from scipy import *
from scipy.signal import *
import array
import csv
import gridfs
import math
import matplotlib.pyplot as plt
import numpy as np
import os
import pymongo
import random
import scipy.stats as stats
import signal
import scikits.statsmodels.api as sm

def plot(original, smoothing):
    # Plot signals 
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.xlabel('Time')
    plt.ylabel('Service Demand')
    
    index = range(0, len(smoothing))
    ax.plot(index, smoothing)
    
    index = range(0, len(original))
    ax.plot(index, original); 
    plt.show();

# TODO: move this to a central location
def load_trace(filename):
    fs = gridfs.GridFS(storage.db, collection='tracefiles')
    
    # Check if this file exists already
    if fs.exists(filename=filename) == False:
        return 
    
    gfile = fs.get_last_version(filename=filename)
    
    trace = trace_pb2.Trace()
    trace.ParseFromString(gfile.read())
    return trace.elements


def exponential():
    trace = load_trace('/O2 RAW business/3')
    
    original = []
    for element in trace: 
        original.append(element.value) 
    
    alpha = 0.3
    smoothing = []
    smoothing.append(0)
    smoothing.append(trace[0].value)
    
    for i in range(2, len(trace)):
        value = float(trace[i - 1].value)
        new_value = alpha * value + (1.0 - alpha) * smoothing[i-1]
        smoothing.append(new_value)

    plot(original, smoothing)



def double_exponential():
    trace = load_trace('/O2 RAW business/3')
    
    original = []
    for element in trace: 
        original.append(element.value) 
    
    alpha = 0.3
    smoothing = []
    smoothing.append(0)
    smoothing.append(trace[0].value)


if __name__ == '__main__':
    exponential()
