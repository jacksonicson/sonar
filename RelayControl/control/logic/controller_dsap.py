from logs import sonarlog
import controller
import json
import numpy as np
from ipmodels import dsap
from numpy import empty, random
from service import times_client
from workload import util as wutil
import control.domains as domains
import sys


######################
## CONFIGURATION    ##
######################
START_WAIT = 120
INTERVAL = 10*60
######################

# Setup logging
logger = sonarlog.getLogger('controller')

class DSAP(controller.LoadBalancer):
    
    def __init__(self, pump, model):
        super(DSAP, self).__init__(pump, model, INTERVAL, START_WAIT)
        print "INIT DSAP"
        self.var = []
        
        # connect to Times
        loadTimeSeries(self)        

# Implement later!
        # initial placement via SSAP        TODO
        # migrationen schedulen via migration list (later with manager)
#        demand_mem = virtual.nodes.DOMAIN_MEM
        # aktuelle zeit
#        time_now = self.pump.sim_time() 
#        self.migrate(domain, source, target, k)        # TODO laeuft parallel >> implement in queue 

        
    def dump(self):
        print 'DSAP controller - Dump configuration...'
        logger.info('Controller Configuration: %s' % json.dumps({'name' : 'DSAP-Controller',
                                                                 'start_wait' : START_WAIT,
                                                                 'interval' : INTERVAL,
                                                                 }))
    def initial_placement_sim(self):
        import placement
        from virtual import nodes
        from control import domains 
        
        nodecount = len(nodes.HOSTS)
        splace = placement.FirstFitPlacement(nodecount, nodes.NODE_CPU, nodes.NODE_MEM, nodes.DOMAIN_MEM)
        migrations, _ = splace.execute()
        
        _nodes = []
        for node in nodes.NODES: 
            mnode = self.model.Node(node, nodes.NODE_CPU_CORES)
            _nodes.append(mnode)
            
        _domains = {}
        for domain in domains.domain_profile_mapping:
            dom = self.model.Domain(domain.domain, nodes.DOMAIN_CPU_CORES)
            _domains[domain.domain] = dom
            
        for migration in migrations:
            print migration 
            _nodes[migration[1]].add_domain(_domains[migration[0]])
            
        return migrations 
    
    def balance(self):
        print 'DSAP-Controller - Balancing'
        
        # B) Fill demand values with data from monitor0.dfg (TimeSteps)
        demand_duration = 24
        service_count = 12
        demand_raw = empty((service_count, demand_duration), dtype=float)

        #TODO
#        domain.ts
#        for i in range(0, len(timeSeries.elements)):
#            time[i] = timeSeries.elements[i].timestamp
#            demand[i] = timeSeries.elements[i].value
            
        for j in xrange(service_count):         
            for t in range(demand_duration):
                demand_raw[j][t] = random.randint(0, 50)    # fill with data from times, profiles
        
        demand_mem=5    #temp, delete 
        
        dsap.solve(12, 100, 100, demand_raw, demand_mem)
        
        
        #sampling
        

    
        
    def post_migrate_hook(self, success, domain, node_from, node_to, end_time):
        print 'DSAP-Controller - Finished'
        if success:
            # Release block
            node_from.blocked = end_time
            node_to.blocked = end_time
            
            # Reset CPU consumption: Necessary because the old CPU readings
            # may trigger another migrations as they do not represent the load
            # without the VM
            node_from.flush(50)
            node_to.flush(50)
            print self.var
        else:
            node_from.blocked = end_time
            node_to.blocked = end_time
            
            
    
def run(self):
    pass    
        
def loadTimeSeries(self):
    print 'Connecting with Times'
    connection = times_client.connect()
    
    self.min_ts_length = sys.maxint # Minimum length across all TS
    freq = 0 # Frequency of the TS from Times 
    
    print "DEBUG: ",self.model.get_hosts(self.model.types.DOMAIN)
    
    # Iterate over all domains and assign them a TS
    for domain in self.model.get_hosts(self.model.types.DOMAIN):
        # Select and load TS (based on the configuration)
        load = domains.cpu_profile_by_name(domain.name)
        print 'loading service: %s ...' % (load)
        
        ts = connection.load(load)
        
        # Convert TS to a numpy array
        # select TS not time index
        freq = ts.frequency
        ts = wutil.to_array(ts)[1]
        
        # Add noise to the time series
        random = np.random.lognormal(mean=0.0, sigma=1.0, size=len(ts))
        ts += random
        ts[ts > 100] = 100
        ts[ts < 0] = 0
        
        # Attach TS to domain 
        domain.ts = ts
        
        print "DEBUG: ",domain.ts
        
        # Update max length
        self.min_ts_length = min(self.min_ts_length, len(ts))
    
    # Close times connection
    times_client.close()
    
    # Reduce length of time series to 6 hours
    self.freq = (freq * 6.0) / 24.0
    
    # Schedule message pump
    self.pump.callLater(0, self.run)
    
    
    
