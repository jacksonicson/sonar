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
        splace = placement.DSAPPlacement(nodecount, nodes.NODE_CPU, nodes.NODE_MEM, nodes.DOMAIN_MEM)
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
            
        
def loadTimeSeries(self):
    pass
    
    
def run(self):
    pass