import configuration
import time

global sim_time
sim_time = 0

def adjust_for_speedup(value):
    if configuration.PRODUCTION:
        return value
    
    return float(value) / float(configuration.SIM_SPEEDUP) 

def time():
    if configuration.PRODUCTION: 
        return time.time()
    
    return sim_time
    
    