from logs import sonarlog
from migration_queue import MigrationQueue
from virtual import nodes
from workload import profiles
import control.domains as domains
import controller
import json
import numpy as np
import virtual.placement as placement

######################
#  CONFIGURATION    ##
######################
NUM_BUCKETS = 6  # Number of allocation buckets
TOTAL_EXPERIMENT_DURATION = profiles.RAMP_UP + profiles.EXPERIMENT_DURATION + profiles.RAMP_DOWN 
PERCENTILE = 90  
######################

# Fixed values
START_WAIT = 0  # Data aggregation phase (ALWAYS 0 FOR THIS CONTROLLER)
INTERVAL = 60  # Frequency of calling balance()

# Setup logging
logger = sonarlog.getLogger('controller')

class Controller(controller.LoadBalancer):
    
    def __init__(self, scoreboard, pump, model):
        super(Controller, self).__init__(scoreboard, pump, model, INTERVAL, START_WAIT)
        
        # Setup migration queue
        # B
        simple = True
        self.migration_queue = MigrationQueue(self, simple, not simple)
        
        # Build allocations
        nodecount = len(nodes.NODES)
        self.placement = placement.DSAPPlacement(nodecount, nodes.NODE_CPU,
                                                 nodes.NODE_MEM, nodes.DOMAIN_MEM)
        self.initial_migrations, self.active_server_info = self.placement.execute(NUM_BUCKETS,
                                                            lambda x: np.percentile(x, PERCENTILE))
            
        # Current bucket
        self.curr_bucket = 0
        
        # Initialization time
        self.time_null = self.pump.sim_time()
        
    def dump(self):
        print 'DSAP controller - Dump configuration...'
        logger.info('Controller Configuration: %s' % json.dumps({'name' : 'DSAP-Controller',
                                                                 'start_wait' : START_WAIT,
                                                                 'interval' : INTERVAL,
                                                                 'num_bucketsl' : NUM_BUCKETS,
                                                                 }))
        
    def initial_placement_sim(self):
        self.build_internal_model(self.initial_migrations)
        return self.initial_migrations 
    
    def initial_placement_production(self):
        return self.initial_migrations, self.active_server_info
    
    def __run_migrations(self, bucket_index):
        # Assignment
        curr_assignment = self.placement.assignment_list[bucket_index]
        
        # Previous assignment
        prev_assignment = self.placement.assignment_list[(bucket_index - 1) % NUM_BUCKETS]
        
        for index_domain in curr_assignment.keys():
            # Get data
            domain_name = domains.domain_profile_mapping[index_domain].domain
            source_node = nodes.get_node_name(prev_assignment[index_domain])
            target_node = nodes.get_node_name(curr_assignment[index_domain])
            
            # Find current node for domain
            source_node = self.model.get_host_for_domain(domain_name).name
            
            # Trigger migration
            model_domain = self.model.get_host(domain_name)
            model_source = self.model.get_host(source_node)
            model_target = self.model.get_host(target_node)
            self.migration_queue.add(model_domain, model_source, model_target)
    
    def __run_optimized_migrations(self, bucket_index):
        # Create allocations lists for GOAP 
        # Assignment
        curr_assignment = self.placement.assignment_list[bucket_index]
        
        # Previous assignment
        prev_assignment = self.placement.assignment_list[(bucket_index - 1) % NUM_BUCKETS]
        
        as_current = [0 for _ in xrange(domains.DOMAINS)]
        as_next = [0 for _ in xrange(domains.DOMAINS)]
        
        for index_domain in xrange(domains.DOMAINS):
            as_current[index_domain] = prev_assignment[index_domain]
            as_next[index_domain] = curr_assignment[index_domain]
                    
        # Get current domain loads
        domain_load = []
        for mapping in domains.domain_profile_mapping:
            domain_name = mapping.domain
            load = self.model.get_host(domain_name).mean_load(20)  # TODO: KValue
            domain_load.append(nodes.to_node_load(load))
                    
        # Schedule migrations
        from ai import astar
        migrations = astar.plan(nodes.NODE_COUNT, as_current, as_next, domain_load)
        
        # Trigger migrations
        dep = None
        for migration in migrations:
            domain_name = domains.domain_profile_mapping[migration[0]].domain
            source_node = nodes.get_node_name(migration[1])
            target_node = nodes.get_node_name(migration[2])
            
            print 'domain %s - source %s - target %s' % (domain_name, source_node, target_node) 
            
            model_domain = self.model.get_host(domain_name)
            model_source = self.model.get_host(source_node)
            model_target = self.model.get_host(target_node)
            
            # dep = self.migration_queue.add(model_domain, model_source, model_target, dep)
            dep = self.migration_queue.add(model_domain, model_source, model_target)
        
        return 
        
    
    def balance(self):
        # Current bucket index
        bucket_duration = TOTAL_EXPERIMENT_DURATION / NUM_BUCKETS
        bucket_index = int((self.pump.sim_time() - self.time_null + profiles.RAMP_UP) / bucket_duration)
        # bucket_index %= NUM_BUCKETS
        print 'bucket index %i' % bucket_index
        if bucket_index >= NUM_BUCKETS:
            return

        # Schedule migrations only once per bucket
        if self.curr_bucket == bucket_index:
            return
        
        # Update current bucket status
        self.curr_bucket = bucket_index
        
        # Trigger migrations to get new bucket allocation
        self.__run_migrations(self.curr_bucket)
        # self.__run_optimized_migrations(self.curr_bucket)
    
    
    def post_migrate_hook(self, success, domain, node_from, node_to, end_time):
        node_from.blocked = self.pump.sim_time() - 1
        node_to.blocked = self.pump.sim_time() - 1
        self.migration_queue.finished(success, domain, node_from, node_to)
    
