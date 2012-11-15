import configuration
import time as systime

global sim_start
sim_start = systime.time() * 1000

def adjust_for_speedup(value):
    if configuration.PRODUCTION:
        return value
    
    return float(value) / float(configuration.SIM_SPEEDUP) 

def time():
    if configuration.PRODUCTION: 
        return time.time()
    
    return float(int((((systime.time() * 1000) - sim_start) * float(configuration.SIM_SPEEDUP)) / 1000))
    
    
    