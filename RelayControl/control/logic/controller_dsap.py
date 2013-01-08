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
START_WAIT = 0
INTERVAL = 60
KVALUE = 10                                     # value given by Andreas
#BUCKET_LENGTH = profiles.EXPERIMENT_DURATION
NUM_BUCKETS = 6
######################

# Setup logging
logger = sonarlog.getLogger('controller')

class DSAP(controller.LoadBalancer):
    
    def __init__(self, pump, model):
        super(DSAP, self).__init__(pump, model, INTERVAL, START_WAIT)
        print "INIT DSAP (length of experiment",profiles.EXPERIMENT_DURATION,", num_buckets=",NUM_BUCKETS,")"
        self.var = []

        
    def dump(self):
        print 'DSAP controller - Dump configuration...'
        logger.info('Controller Configuration: %s' % json.dumps({'name' : 'DSAP-Controller',
                                                                 'start_wait' : START_WAIT,
                                                                 'interval' : INTERVAL,
                                                                 }))
        
    def initial_placement_sim(self):
        import placement as plcmt
        from control import domains 

        nodecount = len(nodes.HOSTS)
        self.placement = plcmt.DSAPPlacement(nodecount, nodes.NODE_CPU, nodes.NODE_MEM, nodes.DOMAIN_MEM)
        migrations, _ = self.placement.execute(NUM_BUCKETS)
        
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
            
            
        # initialize values for balance()
        #self.time_per_bucket = profiles.EXPERIMENT_DURATION / self.placement.buckets_len     # delta for duration per bucket (balance())
            # TODO UMSCHREIBEN!!! fehlerhaft
            
        self.time_per_bucket = self.placement.experiment_length / NUM_BUCKETS
            
        self.time_init = self.pump.sim_time()                                   # time_now synched to beginning of migration
            
        return migrations 
    
    
    def balance(self):
        print 'DSAP-Controller - Balancing'
#        sleep_time = 60                    # TODO later

        time_now = self.pump.sim_time()     # current system time
        
        self.placement.assignment_list
        self.placement.server_list

                
        # calculate current bucket-index from system time
        bucket_index = int((time_now - self.time_init) / self.time_per_bucket) # = allocation index
        
        print 'BUCKET # %i' % bucket_index
        
        if bucket_index == 0:
            return
        
        if bucket_index >= NUM_BUCKETS:      #old: profiles.EXPERIMENT_DURATION /60/60:
            print "End of Bucket"
            return

        _blocked_migrations = 0
            
        for _service in self.placement.assignment_list[ bucket_index ]:
            _server = self.placement.assignment_list[ bucket_index ][ _service ]
            _domain = domains.domain_profile_mapping[ _service ].domain
            
            # domain name for domain ID
            source = self.placement.assignment_list[ bucket_index-1 ] [ _service ]
            target = _server

            _source_node = nodes.get_node_name(source)
            _target_node = nodes.get_node_name(target)

            domain = self.model.get_host(_domain)
            source_node = self.model.get_host(_source_node)
            target_node = self.model.get_host(_target_node)
            
            # prevent parallel migrations (check for blocked servers)
            if time_now < target_node.blocked or time_now < source_node.blocked:
                print "Server locked, for migration:",source_node.name,"->",target_node.name
                _blocked_migrations += 1
                continue
            
            if target_node.domains.has_key(domain.name): #  or not source_node.domains.has_key(_domain):
                continue
            # migrate
            self.migrate(domain, source_node, target_node, KVALUE)
            
        # call test_allocation
        if _blocked_migrations < 1:
            self.test_allocation(bucket_index)
        else:
            print "blocked migrations",_blocked_migrations
            
    def post_migrate_hook(self, success, domain, node_from, node_to, end_time):
        node_from.blocked = self.pump.sim_time() -1
        node_to.blocked = self.pump.sim_time()-1
        if success:
            pass
        else:
            print "MIGRATION FAILED (post_migrate_hook)"
            
    def test_allocation(self, bucket_index):
        
        calculated_allocation = self.placement.assignment_list[ bucket_index ]
        #print "Calculated Allocation:\n",calculated_allocation
                       
        print "Real Allocation:"
        for _service in calculated_allocation:
            
            #retrieve service identifier (targetX)
            _domain = domains.domain_profile_mapping[ _service ].domain     # domain = target
            _server = calculated_allocation[_service]
            server = nodes.get_node_name(_server)
            
            # check if calculated allocation == real allocation
            if _domain in self.model.hosts[server].domains:
                print _domain,"in",server
            else:
                print _domain,"NOT in",server, "[FALSE] !"
        
