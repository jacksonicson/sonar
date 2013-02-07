from analytics import forecasting as smooth
from collector import ttypes
from logs import sonarlog
import json
import numpy as np

################################
# # Configuration              ##
WINDOW = 7000
################################

# Setup logging
logger = sonarlog.getLogger('controller')

# Node types
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

types = enum('NODE', 'DOMAIN')


class Model(object):
    def __init__(self):
        # Holds an internal list of all hosts
        self.hosts = {}
        
    def flush(self):
        self.hosts = {}

    def get_hosts(self, host_type=None):
        if host_type == None:
            return self.hosts.values()
        
        filtered = []
        for host in self.hosts.values():
            if host.type == host_type:
                filtered.append(host) 
        
        return filtered

    def get_host(self, hostname):
        if self.hosts.has_key(hostname):
            return self.hosts[hostname]
        return None


    def get_host_for_domain(self, domain):
        for host in self.get_hosts(types.NODE):
            if host.has_domain(domain):
                return host
        return None


    def server_active_info(self):
        active_count = 0
        active_names = []
        for node in self.get_hosts(types.NODE):
            if node.domains:
                active_names.append(node.name)
                active_count += 1
        
        return active_count, active_names
    
    
    def model_from_current_allocation(self):
        from virtual import allocation
        from virtual import nodes
        allocation = allocation.determine_current_allocation()
        
        for node_name in allocation.iterkeys():
            node = Node(node_name, nodes.NODE_CPU_CORES)
            self.hosts[node_name] = node
            
            for domain_name in allocation[node_name]:
                domain = Domain(domain_name, nodes.DOMAIN_CPU_CORES)
                node.add_domain(domain)
                self.hosts[domain] = domain


    def model_from_migrations(self, migrations):
        from virtual import nodes
        from control import domains
        _nodes = []
        for node in nodes.NODES: 
            mnode = Node(node, nodes.NODE_CPU_CORES)
            self.hosts[node] = mnode
            _nodes.append(mnode)
            
        _domains = {}
        for domain in domains.domain_profile_mapping:
            dom = Domain(domain.domain, nodes.DOMAIN_CPU_CORES)
            self.hosts[domain.domain] = dom
            _domains[domain.domain] = dom
            
        for migration in migrations:
            _nodes[migration[1]].add_domain(_domains[migration[0]])
    
    def dump(self):
        print 'Dump controller initial model configuration...'
        json_map = {}
        for node in self.get_hosts(host_type=types.NODE):
            print 'Node: %s' % (node.name)
            json_map[node.name] = []
            for domain in node.domains.values():
                print '   Domain: %s' % domain.name
                json_map[node.name].append(domain.name)
                
        logger.info('Controller Initial Model: %s' % json.dumps(json_map))
    

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
    
#    def __eq__(self, other):
#        if other == None:
#            return
#        return other.name == self.name        
    
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
                
        # Type of this object
        self.type = types.DOMAIN
        
    def get_watch_filter(self):
        return ttypes.SensorToWatch(self.name, 'psutilcpu')
    

class Node(__Host):
    def __init__(self, name, cores):
        super(Node, self).__init__(name, cores)
                
        # Type of this object
        self.type = types.NODE
        
        # Migrations
        self.active_migrations_out = 0
        self.active_migrations_in = 0
        
        # Holds a mapping of domains
        self.domains = {}
    
    def add_domain(self, domain):
        self.domains[domain.name] = domain
        
    def has_domain(self, domain):
        return self.domains.has_key(domain)
        
    def get_watch_filter(self):
        return ttypes.SensorToWatch(self.name, 'psutilcpu')
    
    def dump(self):
        domains = ', '.join(self.domains.keys())
        print 'Host: %s Load: %f Volume: %f Domains: %s' % (self.name, self.mean_load(5), self.volume, domains)





    


