import numpy as np
import util
from timeutil import * #@UnusedWildImport
import matplotlib.pyplot as plt
import plot

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


MOD0 = []
MOD1 = [
        Element(hour(10), hour(4), 30)
        ]
MOD2 = [
        Element(hour(0), hour(3), 20),
        Element(hour(9), hour(2), 60),
        Element(hour(13), hour(2), 30),
        Element(hour(21), hour(3), 20),
        ]
MOD3 = [
        Element(hour(9), hour(1), 10),
        Element(hour(10), hour(2), 40),
        Element(hour(12), hour(2), -20),
        Element(hour(14), hour(1), -10),
        ]
MOD4 = [
        Element(hour(0), hour(8), 5),
        Element(hour(8), hour(10), 30),
        Element(hour(18), hour(6), 10),
        ]
MOD5 = [
        Element(hour(10), hour(1), 40),
        ]
MOD6 = [
        Element(hour(8), hour(10), -10),
        ]
MOD7 = [
        Element(hour(7), hour(3), -50),
        Element(hour(10), hour(12), -20),
        ]
MOD8 = [
        Element(hour(0), hour(8), 5),
        Element(hour(8), hour(10), 60),
        Element(hour(18), hour(6), 10),
        ]

def __generate_mod_ts(demand, modification, interval_length):
    result = np.zeros((len(demand),))
    
    for element in modification:
        i = lambda t: int(t / interval_length)
        i_start = i(element.start)
        i_end = i(element.start + element.width)
        result[i_start : i_end] = element.height

    # Smoothing
    window = 20
    weights = np.repeat(1.0, window) / window
    result = np.convolve(result, weights)[0:-1 * window + 1 ]
    
    mu, sigma = 0, 2
    a = np.random.normal(mu,sigma, len(demand))
    result += a
    
    # Divide for multiplication
    result /= 100.0
    
    return result

def generate_TS(demand, modification, interval_length):
    result = __generate_mod_ts(demand, modification, interval_length)
    
    # Apply result to the demand curve by multiplication
    demand += demand * result
    return demand
    
def stretch(demand, f=1.0):
    f_start = int((len(demand) - (len(demand) / f)) / 2)
    stretch = np.zeros(len(demand)) 
    for i in xrange(len(demand)):
        stretch[i] = demand[f_start + int(i / f)]
        
    return stretch
    
def scale(demand, f=1.0):
    demand *= f
    return demand
    
def limit(demand, limit=100):
    exp = demand > limit
    demand[exp] = 100
    return demand
    
def add_modifier(time, demand, interval, modifier, _scale):
    demand = generate_TS(demand, modifier, interval)
    
    demand = stretch(demand, _scale[0])
    demand = scale(demand, _scale[1])
    
    return limit(demand)

def process_trace(connection, name, modifier, scale, interval=None, cycle_time=None):
    timeSeries = connection.load(name)
    time, demand = util.to_array(timeSeries)
    interval = timeSeries.frequency
    return add_modifier(time, demand, interval, modifier, scale), timeSeries.frequency


def __plot():
    modifications = [MOD0, MOD1, MOD2, MOD3, MOD4, MOD5,
                     MOD6, MOD7, MOD8]
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_xlabel('Time in minutes')
    ax.set_ylabel('Change factor')
    
    
    for mod in modifications:
        demand = np.zeros(288)
        result = __generate_mod_ts(demand, mod, minu(5))
        ax.plot(range(0, len(result)*5, 5), result, linewidth=0.7)
        
    # plt.show()
    plot.rstyle(ax)
    plt.savefig('C:/temp/convolution/modifiers.png')

def main():
    __plot() 

if __name__ == '__main__':
    main()
