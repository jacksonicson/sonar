from logs import sonarlog
import controller
import json
import numpy as np
from ipmodels import dsap
from numpy import empty, random
from service import times_client
from workload import util as wutil
from workload import profiles
from virtual import nodes
import control.domains as domains
import sys
from control.logic.placement import Placement
from control.logic import placement
import service
import math


######################
## CONFIGURATION    ##
######################
START_WAIT = 120
INTERVAL = 10*60
kvalue = 10             # value given by Andreas

######################

# Setup logging
logger = sonarlog.getLogger('controller')

class DSAP(controller.LoadBalancer):
    
    def __init__(self, pump, model):
        super(DSAP, self).__init__(pump, model, INTERVAL, START_WAIT)
        print "INIT DSAP"
        self.var = []
        
# Implement later!
        # migrationen schedulen via migration list (later with manager)

        
    def dump(self):
        print 'DSAP controller - Dump configuration...'
        logger.info('Controller Configuration: %s' % json.dumps({'name' : 'DSAP-Controller',
                                                                 'start_wait' : START_WAIT,
                                                                 'interval' : INTERVAL,
                                                                 }))
        
    def initial_placement_sim(self):
        import placement as plcmt
        from control import domains 
        
        global placement

        nodecount = len(nodes.HOSTS)
        placement = plcmt.DSAPPlacement(nodecount, nodes.NODE_CPU, nodes.NODE_MEM, nodes.DOMAIN_MEM)
        migrations, _ = placement.execute()
        
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
            
            
        # initialising values for balance()
        _total_bucket_length = 6 * 60 * 60
        self.time_per_bucket = _total_bucket_length / placement.buckets_len     # delta for duration per bucket (balance())
        self.time_init = self.pump.sim_time()                                   # time_now synched to beginning of migration
            
        return migrations 
    
    
    def balance(self):
        print 'DSAP-Controller - Balancing'
#        sleep_time = 60                    # TODO later

        time_now = self.pump.sim_time()     # current system time
        
        placement.assignment_list
        placement.server_list

                
        # calculate current index for current time
        _bucket_number = (time_now - self.time_init) / self.time_per_bucket  
        
        _index = int(math.floor(_bucket_number))     
        print "DEBUG: ",_bucket_number," = Bucket#",_index
        
        if _index < 0.5:    #break for T=0, since there will be no source-destination of T=-1
            return
        
        print "DEBUG: Allocation, T =", _index
        print "DEBUG: assignment_list[",_index,"]:",placement.assignment_list[ _index ]
#            print "DEBUG ",placement.assignment_list[ _allocation ]
            
        for _service in placement.assignment_list[ _index ]:
            _server = placement.assignment_list[ _index ][ _service ]

            domain = domains.domain_profile_mapping[ _service ].domain
            
            # domain name for domain ID
            source = placement.assignment_list[ _index-1 ] [ _service ]
            target = _server

            if (source != target):
                print _service,"->",_server,"(triggered migration)"
                self.migrate(domain, source, target, kvalue)
            else:
                print _service,"->",_server


#        target = nodes.get_node_name(i)

#DEBUG
#        for domain in domains.domain_profile_mapping:
#            print "DEBUG domain",i,"=",domain.domain
#            i+=1
            
            # TODO laeuft parallel >> implement in queue
            
            
            
    def post_migrate_hook(self, success, domain, node_from, node_to, end_time):
        if success:
            print "SUCCESSFUL MIGRATION (DEBUG)"
        else:
            print "MIGRATION FAILED (DEBUG)"
