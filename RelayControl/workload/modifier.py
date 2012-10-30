import math
import numpy as np
import util

class Element(object):
    def __init__(self, start, width, height, top_width=None):
        '''
        Define an workload modification element which starts at start minutes,
        ends at end minutes has a height in absolute percfent and a top width:
             topWidth
           +----------+
           |          |
           |          | height
        ---+          +-----
         start       end
        '''
        
        if top_width == None:
            top_width = width
        
        self.start = start
        self.width = width
        self.height = height
        self.top_width = top_width


def generate_TS(demand, modification, length, interval_length):
    result = np.zeros((length,))
    
    for element in modification:
        i = lambda t: int(t / interval_length)
        i_start = i(element.start)
        i_end = i(element.start + element.width)
        result[i_start : i_end] = element.height

    # Smoothing
    window = 5
    weights = np.repeat(1.0, window) / window
    result = np.convolve(result, weights)[0:-1 * window + 1 ]
    
    # Divide for multiplication
    result /= 100.0
    
    # Apply result to the demand curve by multiplication
    demand += demand * result    
    
    

def add_modifier(time, demand, interval):
    modification0 = [
                 Element(150, 200, 20),
                 Element(400, 100, -50),
                 Element(500, 50, +30),
                 #Element(550, 50, +30),
                 ]
    
    generate_TS(demand, modification0, len(demand), interval)
    
    return demand

def process_trace(connection, name, interval=None, cycle_time=None):
    timeSeries = connection.load(name)
    time, demand = util.to_array(timeSeries)
    interval = timeSeries.frequency / 60
    print interval
    return add_modifier(time, demand, interval), timeSeries.frequency
