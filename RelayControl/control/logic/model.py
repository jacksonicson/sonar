import numpy as np
from collector import ttypes

################################
## Configuration              ##
WINDOW = 10
################################

# Holds an internal list of all hosts
hosts = {}

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

types = enum('NODE', 'DOMAIN')

def get_hosts():
    return hosts.values()

def get_host(hostname):
    if hosts.has_key(hostname):
        return hosts[hostname]
    return None

class Host(object):
    
    def __init__(self):
        self.readings = [0 for _ in xrange(0, WINDOW)]
        self.counter = 0
        self.volume = 0
        self.overloaded = False
        self.underloaded = False
        
        self.blocked = 0
        
    def put(self, reading):
        self.readings[self.counter] = reading.value
        self.counter = (self.counter + 1) % WINDOW
        
    def mean_load(self):
        return np.mean(self.readings)
    
    def get_readings(self):
        index = (self.counter) % WINDOW
        result = []
        for _ in xrange(WINDOW):
            result.append(self.readings[index])
            index = (index + 1) % WINDOW
            
        return result
    
    def predict(self):
        return 100
    
    def handle_overload(self):
        pass
        
    
class Domain(Host):
    def __init__(self, name):
        super(Domain, self).__init__()
        hosts[name] = self
        
        self.name = name
        self.type = types.DOMAIN
        self.ts = None
        
    def get_watch_filter(self):
        return ttypes.SensorToWatch(self.name, 'psutilcpu')
    


class Node(Host):
    def __init__(self, name):
        super(Node, self).__init__()
        hosts[name] = self
        
        self.name = name
        self.domains = {}
        self.type = types.NODE
    
    def add_domain(self, domain):
        self.domains[domain.name] = domain
        
    def get_watch_filter(self):
        return ttypes.SensorToWatch(self.name, 'psutilcpu')
    
    def dump(self):
        domains = ', '.join(self.domains.keys())
        print 'Host: %s Load: %f Volume: %f Domains: %s' % (self.name, self.mean_load(), self.volume, domains)




