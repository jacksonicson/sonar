from analytics import forecasting as smooth
from collector import ttypes
from logs import sonarlog
import json
import numpy as np

################################
## Configuration              ##
WINDOW = 7000
################################

# Holds an internal list of all hosts
hosts = {}

# Setup logging
logger = sonarlog.getLogger('controller')

def flush():
    global hosts
    hosts = {}

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

types = enum('NODE', 'DOMAIN')

def get_hosts(host_type=None):
    if host_type == None:
        return hosts.values()
    
    filtered = []
    for host in hosts.values():
        if host.type == host_type:
            filtered.append(host) 
    
    return filtered

def get_host(hostname):
    if hosts.has_key(hostname):
        return hosts[hostname]
    return None


def server_active_info():
    active_count = 0
    active_names = []
    for node in get_hosts(types.NODE):
        if node.domains:
            active_names.append(node.name)
            active_count += 1
    
    return active_count, active_names
    

class __Host(object):
    '''
    This is a private class which should not be used outside of this
    module. It is the base method for all entities representing concrete
    elements of the infrastructure.  
    '''
    
    def __init__(self, name, cores):
        self.name = name
        
        # Number of cores 
        self.cpu_cores = cores
        
        # Stores readings over the window
        self.readings = [0 for _ in xrange(0, WINDOW)]
        
        # Current index in the ring buffer
        self.counter = 0
        
        # Double exponential smoothing parameters
        self.globalCounter = 0
        self.f_t = 0
        self.c_t = 0
        self.T_t = 0
        
    def put(self, reading):
        self.readings[self.counter] = reading.value
        self.counter = (self.counter + 1) % WINDOW
        
        # Calculates double exponential smoothing
        if self.globalCounter == 2:
            self.c_t = float(self.readings[0]) 
            self.T_t = float(self.readings[1] - self.readings[0])
            self.f_t = self.c_t + self.T_t
            self.globalCounter += 1
        elif self.globalCounter > 2:
            self.f_t, self.c_t, self.T_t = smooth.continuouse_double_exponential_smoothed(self.c_t,
                                                                       self.T_t,
                                                                       reading.value)
        else:
            self.globalCounter += 1
            
    
    def forecast(self):
        return self.f_t
    
    def flush(self, value=0):
        self.readings = [value for _ in xrange(0, WINDOW)]
        
    def mean_load(self, k=None):
        if k == None:
            return np.mean(self.readings)
        
        sorted_readings = self.get_readings()
        return np.mean(sorted_readings[-k:])
    
    def percentile_load(self, percentile, k=None):
        if k == None:
            sorted_readings = self.readings
        else:
            sorted_readings = self.get_readings()[-k:]
        
        return np.percentile(sorted_readings, percentile)
    
    
    def get_readings(self):
        index = (self.counter) % WINDOW
        result = []
        for _ in xrange(WINDOW):
            result.append(self.readings[index])
            index = (index + 1) % WINDOW
            
        return result
    
        
    
class Domain(__Host):
    def __init__(self, name, cores):
        super(Domain, self).__init__(name, cores)
        
        # Adds itself to the hosts list
        hosts[name] = self
        
        # Type of this object
        self.type = types.DOMAIN
        
    def get_watch_filter(self):
        return ttypes.SensorToWatch(self.name, 'psutilcpu')
    

class Node(__Host):
    def __init__(self, name, cores):
        super(Node, self).__init__(name, cores)
        
        # Adds itself to the hosts list
        hosts[name] = self
        
        # Type of this object
        self.type = types.NODE
        
        # Migrations
        self.active_migrations_out = 0
        self.active_migrations_in = 0
        
        # Holds a mapping of domains
        self.domains = {}
    
    def add_domain(self, domain):
        self.domains[domain.name] = domain
        
    def get_watch_filter(self):
        return ttypes.SensorToWatch(self.name, 'psutilcpu')
    
    def dump(self):
        domains = ', '.join(self.domains.keys())
        print 'Host: %s Load: %f Volume: %f Domains: %s' % (self.name, self.mean_load(5), self.volume, domains)



def dump():
    print 'Dump controller initial model configuration...'
    json_map = {}
    for node in get_hosts(host_type=types.NODE):
        print 'Node: %s' % (node.name)
        json_map[node.name] = []
        for domain in node.domains.values():
            print '   Domain: %s' % domain.name
            json_map[node.name].append(domain.name)
            
    logger.info('Controller Initial Model: %s' % json.dumps(json_map))

    


