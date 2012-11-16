import configuration
import time as systime
import math 

global sim_start
sim_start = systime.time()

def adjust_for_speedup(value):
    if configuration.PRODUCTION:
        return value
    
    return float(value) / float(configuration.SIM_SPEEDUP) 


def time():
    if configuration.PRODUCTION: 
        return time.time()
    
    sim_time = systime.time() - sim_start
    sim_time *= float(configuration.SIM_SPEEDUP)
    return math.ceil(sim_time)

 
def domain_to_server_cpu(self, target, domain, domain_cpu):
        domain_cpu_factor = target.cpu_cores / domain.cpu_cores
        return domain_cpu / domain_cpu_factor

