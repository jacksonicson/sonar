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
KVALUE = 10             # value given by Andreas

######################

# Setup logging
logger = sonarlog.getLogger('controller')

class DSAP(controller.LoadBalancer):
    
    def __init__(self, pump, model):
        super(DSAP, self).__init__(pump, model, INTERVAL, START_WAIT)
        print "INIT DSAP"
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
            
            
        # initialize values for balance()
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

                
        # calculate current bucket-index from system time
        bucket_index = int((time_now - self.time_init) / self.time_per_bucket)
        
        print 'BUCKET # %i' % bucket_index

            
        for _service in placement.assignment_list[ bucket_index ]:
            _server = placement.assignment_list[ bucket_index ][ _service ]

            _domain = domains.domain_profile_mapping[ _service ].domain
            
            # domain name for domain ID
            source = placement.assignment_list[ bucket_index-1 ] [ _service ]
            target = _server

            _source_node = nodes.get_node_name(source)
            _target_node = nodes.get_node_name(target)

            domain = self.model.get_host(_domain)
            source_node = self.model.get_host(_source_node)
            target_node = self.model.get_host(_target_node)
            
            # prevent parallel migrations (check for blocked servers)
            if time_now < target_node.blocked or time_now < source_node.blocked:
                print "Server locked, for migration:",source_node.name,"->",target_node.name
                continue
            
            if target_node.domains.has_key(domain.name): #  or not source_node.domains.has_key(_domain):
                continue
            
            # migrate
            self.migrate(domain, source_node, target_node, KVALUE)

            
    def post_migrate_hook(self, success, domain, node_from, node_to, end_time):
        node_from.blocked = self.pump.sim_time() -1
        node_to.blocked = self.pump.sim_time()-1
        if success:
            pass
        else:
            print "MIGRATION FAILED (post_migrate_hook)"
            
