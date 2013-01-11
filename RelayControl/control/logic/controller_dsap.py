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
from virtual.placement import Placement
from virtual import placement
import service
import math
from migration_scheduler import migration


######################
# # CONFIGURATION    ##
######################
START_WAIT = 0
INTERVAL = 60
KVALUE = 10  # value given by Andreas
NUM_BUCKETS = 6
######################

# Setup logging
logger = sonarlog.getLogger('controller')

class DSAP(controller.LoadBalancer):
    
    def __init__(self, pump, model):
        super(DSAP, self).__init__(pump, model, INTERVAL, START_WAIT)
        print "INIT DSAP (length of experiment", profiles.EXPERIMENT_DURATION, ", num_buckets=", NUM_BUCKETS, ")"
        self.var = []
        self.migration_queue = migration(self, KVALUE)

        
    def dump(self):
        print 'DSAP controller - Dump configuration...'
        logger.info('Controller Configuration: %s' % json.dumps({'name' : 'DSAP-Controller',
                                                                 'start_wait' : START_WAIT,
                                                                 'interval' : INTERVAL,
                                                                 'k_value' : KVALUE,
                                                                 'num_bucketsl' : NUM_BUCKETS,
                                                                 }))
        
    def initial_placement_sim(self):
        import virtual.placement as plcmt

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
            
        # TODO DOKUMENTIEREN
        self.time_per_bucket = self.placement.experiment_length / NUM_BUCKETS
        # TODO DOKUMENTIEREN
        self.time_init = self.pump.sim_time()
            
        return migrations 
    
    
    def balance(self):
        time_now = self.pump.sim_time()  # current system time
        
        self.placement.assignment_list
        self.placement.server_list

        # calculate current bucket-index from system time
        bucket_index = int((time_now - self.time_init) / self.time_per_bucket)  # = allocation index
        
        print 'BUCKET # %i' % bucket_index
        if bucket_index == 0:
            return
        if bucket_index >= NUM_BUCKETS:
            print "End of Bucket"
            return
        
        if not self.migration_queue.empty():
            return

        # TODO: Muss in eigene Methode calc_migrations(current_allocation, next_allocation) - returns list of migrations
        for _service in self.placement.assignment_list[ bucket_index ]:
            _server = self.placement.assignment_list[ bucket_index ][ _service ]
            _domain = domains.domain_profile_mapping[ _service ].domain
            
            # domain name for domain ID
            source = self.placement.assignment_list[ bucket_index - 1 ] [ _service ]
            target = _server

            _source_node = nodes.get_node_name(source)
            _target_node = nodes.get_node_name(target)

            domain = self.model.get_host(_domain)
            source_node = self.model.get_host(_source_node)
            target_node = self.model.get_host(_target_node)
            
            # TODO: Iterate over all migrations and fil them to migration queue
            self.migration_queue.add_migration(domain, source_node, target_node, 'null')
            
    
    
    def post_migrate_hook(self, success, domain, node_from, node_to, end_time):
        node_from.blocked = self.pump.sim_time() - 1
        node_to.blocked = self.pump.sim_time() - 1
        
        # TODO ueberpruefen ob die Migration Queue die blocks schon setzt / aufhebt
        self.migration_queue.finish_migration(success, domain, node_from, node_to)
    
    
    def test_allocation(self, bucket_index):        
        calculated_allocation = self.placement.assignment_list[ bucket_index ]
                       
        print "Allocation check:"
        for _service in calculated_allocation:
            
            # retrieve service identifier (targetX)
            _domain = domains.domain_profile_mapping[ _service ].domain  # domain = service = target
            _node = calculated_allocation[_service]  # node = server
            node = nodes.get_node_name(_node)
            
            # check if calculated allocation == real allocation
            if _domain in self.model.hosts[node].domains:
                print _domain, "in", node
            else:
                print _domain, "NOT in", node, "[ALLOCATION FAILURE] !"
        
