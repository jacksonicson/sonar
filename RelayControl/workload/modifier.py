import util
import numpy as np

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
    result += 100
    
    import math
    for element in modification:
        i = lambda t: int(t / interval_length)
        if element.top_width < element.width:  
            i_start = i(element.start)
            
            m = (2 * element.height) / (element.width - element.top_width)
            f = lambda t: m * t
            
            if m > 0:
                i_end_slope = int(math.ceil(element.height / (m * interval_length)))
            else:
                i_end_slope = i_start
                
            i_end_top = i_end_slope + i(element.top_width)  
            
            result[i_start + i_end_slope : i_start + i_end_top] = element.height
            for i in xrange(i_end_slope):
                height_i = f(i * interval_length)
                result[i_start + i] = height_i
                print 'as %i' % i
                
                height_i = -1 *  f(i * interval_length) + element.height
                result[i_start + i_end_top + i] = height_i
                print 'b %i' % i
        else:
            i_start = i(element.start)
            i_end = i(element.start + element.width)
            result[i_start : i_end] = element.height
            
    result /= 100.0
    demand += demand * result    
    
    print demand
    

def add_modifier(time, demand):
    modification0 = [
                 Element(0, 50, 12),
                 ]
    
    print demand
    print (len(demand) * 5) / 60 # this one has 24 hours
    generate_TS(demand, modification0, len(demand), 5)
    
    return demand

def process_trace(connection, name):
    timeSeries = connection.load(name)
    time, demand = util.to_array(timeSeries)
    return add_modifier(time, demand)
