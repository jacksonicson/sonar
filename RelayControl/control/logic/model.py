import numpy as np
from collector import ttypes

################################
## Configuration              ##
WINDOW = 200
################################

# Holds an internal list of all hosts
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

class __Host(object):
    '''
    This is a private class which should not be used outside of this
    module. It is the base method for all entities representing concrete
    elements of the infrastructure.  
    '''
    
    def __init__(self, name):
        self.name = name
        
        # Stores readings over the window
        self.readings = [0 for _ in xrange(0, WINDOW)]
        
        # Current index in the ring buffer
        self.counter = 0
        
    def put(self, reading):
        self.readings[self.counter] = reading.value
        self.counter = (self.counter + 1) % WINDOW
    
    def flush(self):
        self.readings = [0 for _ in xrange(0, WINDOW)]
        
    def mean_load(self, k=None):
        if k == None:
            return np.mean(self.readings)
        
        sorted_readings = self.get_readings()
        return np.mean(sorted_readings[-k:])
    
    def get_readings(self):
        index = (self.counter) % WINDOW
        result = []
        for _ in xrange(WINDOW):
            result.append(self.readings[index])
            index = (index + 1) % WINDOW
            
        return result
    
        
    
class Domain(__Host):
    def __init__(self, name):
        super(Domain, self).__init__(name)
        
        # Adds itself to the hosts list
        hosts[name] = self
        
        # Type of this object
        self.type = types.DOMAIN
        
    def get_watch_filter(self):
        return ttypes.SensorToWatch(self.name, 'psutilcpu')
    

class Node(__Host):
    def __init__(self, name):
        super(Node, self).__init__(name)
        
        # Adds itself to the hosts list
        hosts[name] = self
        
        # Type of this object
        self.type = types.NODE
        
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
    for node in get_hosts(host_type=types.NODE):
        print 'Node: %s' % (node.name)
        for domain in node.domains.values():
            print '   Domain: %s' % domain.name


