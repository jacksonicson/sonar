from configuration import storage
from proto import trace_pb2
from scipy import *
from scipy.signal import *
import array
import csv
import gridfs
import math
import matplotlib.colors as c
import matplotlib.pyplot as plt
import numpy as np
import os
import pymongo
import random
import scipy.stats as stats
import signal


def load_results(suite):
    json_obj = {
                'suite' : suite,
                'loader' : 'de.tum.in.dss.target.dsaps.DsapsLaunchConfiguration',
                # 'status' : 'running', # TODO: Change
                }
    targets = storage.targets.find(json_obj)
    
    results = []
    customs = []
    
    for run_target in targets:
        print 'target'
        try:
            run_target['results']
        except KeyError:
            print 'no results'
            continue
        
        results.append(run_target['results'])
        customs.append(run_target['custom'])
    
    return customs, results


def load_trace(filename):
    fs = gridfs.GridFS(storage.db, collection='tracefiles')
    
    # Check if this file exists already
    if fs.exists(filename=filename) == False:
        return 
    
    gfile = fs.get_last_version(filename=filename)
    
    trace = trace_pb2.Trace()
    trace.ParseFromString(gfile.read())
    
    result = []
    for element in trace.elements:
        result.append(element.value)
    
    return result


def plot_segment(ax, service_id, signal, start, end):
    
    colors = ['#FF0000', '#00FFFF', '#0000FF', '#0000A0', '#FF0080',
               '#FF0000', '#00FFFF', '#0000FF', '#0000A0', '#FF0080',
               '#FF0000', '#00FFFF', '#0000FF', '#0000A0', '#FF0080',
               '#FF0000', '#00FFFF', '#0000FF', '#0000A0', '#FF0080',
               '#FF0000', '#00FFFF', '#0000FF', '#0000A0', '#FF0080',]
    
    index = range(start, end)
    subsignal = signal[start:end]
    ax.scatter(index, subsignal, color=colors[service_id], marker='x')
    

def plot_signal(ax, signal):
    ax.plot(range(0, len(signal)), signal)
    

def main(filename):
    customs, results = load_results('configuration1318588181')
    
    for target in range(0, len(customs)):
        # Get the custom and result element form this target
        result = results[target]
        custom = customs[target]
        server_count = len(custom['servers'])
        
        # Load signals for this target
        signals = []
        for signal_name in custom['traces']:
            signal = load_trace(signal_name)
            signals.append(signal)
        
        # setup the new plot
        fig = plt.figure()
        fig.set_size_inches((10, 10))
        plt.xlabel('Time')
        plt.ylabel('Service Demand')
        
        # create a new subplot for each server
        axes = []
        for a in range(0, server_count):
            val = int('%i%i%i' % (server_count, 1, a + 1))
            print val
            ax = fig.add_subplot(server_count, 1, a + 1)
            ax.set_title('Server %i' % (a));
            
            ax.set_xlim(0, 24)
            ax.set_ylim(0, 1)
            
            axes.append(ax)
        
        
        # Render the signals
        allocations = result['allocations']
        
        # accumulated load
        accumulation = [[0 for col in range(0, len(allocations))] for row in range(0, server_count)]
        
        for time in range(0, len(allocations)):
            
            servers = allocations[time]
            for server_id in range(0, server_count):
                
                sum = 0
                
                services = servers[server_id]
                for service_id in services:
                    plot_segment(axes[server_id], service_id, signals[service_id], time, time + 1)
                    sum += signals[service_id][time]

                accumulation[server_id][time] = sum
                
        print accumulation
        # Plot accumulated data
        for server in range(0, len(accumulation)):
            acc_signal = accumulation[server]
            plot_signal(axes[server], acc_signal)

        
        plt.show()
        fname = '%s%i.png' % (filename, target)
        fname = fname.replace('/', '_')
        print 'writing %s...' % (fname)
        fig.savefig('../../target/%s' % (fname))
                

if __name__ == '__main__':
    main('consolidation')
