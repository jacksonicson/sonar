from logs import sonarlog
from migration_queue import MigrationQueue
from virtual import nodes
import control.domains as domains
import controller
import json
import virtual.placement as placement

######################
# # CONFIGURATION    ##
######################
START_WAIT = 0
INTERVAL = 60
NUM_BUCKETS = 12
######################

# Setup logging
logger = sonarlog.getLogger('controller')

class Controller(controller.LoadBalancer):
    
    def __init__(self, pump, model):
        super(Controller, self).__init__(pump, model, INTERVAL, START_WAIT)
        
        # Setup migration queue
        self.migration_queue = MigrationQueue(self)
        
        # Build allocations
        nodecount = len(nodes.NODES)
        self.placement = placement.DSAPPlacement(nodecount, nodes.NODE_CPU,
                                                 nodes.NODE_MEM, nodes.DOMAIN_MEM)
        self.initial_migrations, _ = self.placement.execute(NUM_BUCKETS)
            
        # Current bucket
        self.curr_bucket = 0
        
        # Allocation cycle duration
        self.time_per_bucket = self.placement.experiment_length / NUM_BUCKETS
        
        # Initialization time
        self.time_init = self.pump.sim_time()
        
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
    
    def __run_migrations(self, bucket_index):
        print bucket_index
        # Assignment
        curr_assignment = self.placement.assignment_list[bucket_index]
        
        # Previous assignment
        prev_assignment = self.placement.assignment_list[(bucket_index - 1) % NUM_BUCKETS]
        
        for index_domain in curr_assignment.keys():
            # Get data
            domain_name = domains.domain_profile_mapping[index_domain].domain
            source_node = nodes.get_node_name(prev_assignment[index_domain])
            target_node = nodes.get_node_name(curr_assignment[index_domain])
            
            # Trigger migration
            model_domain = self.model.get_host(domain_name)
            model_source = self.model.get_host(source_node)
            model_target = self.model.get_host(target_node)
            self.migration_queue.add(model_domain, model_source, model_target)
    
    def balance(self):
        # Current bucket index
        bucket_index = int((self.pump.sim_time() - self.time_init) / self.time_per_bucket)
        #bucket_index %= NUM_BUCKETS
        if bucket_index >= NUM_BUCKETS:
            return

        # Schedule migrations only once per bucket
        if self.curr_bucket == bucket_index:
            return
        
        # Update current bucket status
        self.curr_bucket = bucket_index
        
        # Trigger migrations to get new bucket allocation
        self.__run_migrations(self.curr_bucket)
    
    
    def post_migrate_hook(self, success, domain, node_from, node_to, end_time):
        node_from.blocked = self.pump.sim_time() - 1
        node_to.blocked = self.pump.sim_time() - 1
        self.migration_queue.finished(success, domain, node_from, node_to)
    
    
    # TODO: Rewrite this stuff so that it fits with the refactored dsap controller above
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
        
