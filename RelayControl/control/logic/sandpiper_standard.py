from logs import sonarlog
import json
import controller
import placement
import migration_scheduler
import controller_imbalance
import controller_reactive
import controller_swap
from virtual import nodes

######################
## CONFIGURATION    ##
######################
START_WAIT = 120
INTERVAL = 300
THRESHOLD_OVERLOAD = 90
THRESHOLD_UNDERLOAD = 40
PERCENTILE = 80.0
THRESHOLD_IMBALANCE = 0.12
MIN_IMPROVEMENT_IMBALANCE = 0.01
NODE_CAPACITY = 100 #to be checked
K_VALUE = 20 # sliding windows size
M_VALUE = 17 # m values out of the window k must be above or below the threshold

# MIXED CONTROLLER SETTINGS
# Values can be 'imbalance', 'reactive', 'swap' or ''
CONTROLLER_SETTINGS = {
'first_controller' : 'imbalance',
'second_controller' : 'reactive',
'third_controller' : 'swap'
}

######################

# Setup logging
logger = sonarlog.getLogger('controller')

class Sandpiper(controller.LoadBalancer):
    
    def __init__(self, pump, model):
        super(Sandpiper, self).__init__(pump, model, INTERVAL, START_WAIT)
        self.migration_scheduler = migration_scheduler.migration(self, K_VALUE)
        self.migration_triggered = False
        self.controller_setup = {}
        
        for position,setting in CONTROLLER_SETTINGS.iteritems():
            if setting == 'imbalance':
                self.controller_setup[position] = self.imbalance_controller
            elif setting == 'reactive':
                self.controller_setup[position] = self.reactive_controller
            elif setting == 'swap':
                self.controller_setup[position] = self.swap_controller
            else:
                self.controller_setup[position] = self.static_controller
            
    def initial_placement_sim(self):
        nodecount = len(nodes.HOSTS)
        splace = placement.FirstFitPlacement(nodecount, nodes.NODE_CPU, nodes.NODE_MEM, nodes.DOMAIN_MEM)
        migrations, _ = splace.execute()
        self.build_internal_model(migrations)       
            
        return migrations
        
    def post_migrate_hook(self, success, domain, node_from, node_to, end_time):
        if success:
            # Release block
            node_from.blocked = end_time
            node_to.blocked = end_time
            
            # Reset CPU consumption: Necessary because the old CPU readings
            # may trigger another migrations as they do not represent the load
            # without the VM
            node_from.flush(50)
            node_to.flush(50)
            
            # Remove migration from queue
            self.migration_scheduler.finish_migration(success, domain, node_from, node_to)
        else:
            # Remove migration from queue
            self.migration_scheduler.finish_migration(success, domain, node_from, node_to)

            time_now = self.pump.sim_time()
            node_from.blocked = time_now
            node_to.blocked = time_now
        
    def dump(self):
        print 'Dump Sandpiper controller configuration...'
        logger.info('Controller Configuration: %s' % json.dumps({'name' : 'Sandpiper',
                                                                 'start_wait' : START_WAIT,
                                                                 'interval' : INTERVAL,
                                                                 'threshold_overload' : THRESHOLD_OVERLOAD,
                                                                 'threshold_underload' : THRESHOLD_UNDERLOAD,
                                                                 'percentile' : PERCENTILE,
                                                                 'k_value' :K_VALUE,
                                                                 'm_value' : M_VALUE
                                                                 }))    
    
    def balance(self):
        sleep_time = 60
        time_now = self.pump.sim_time()
        
        self.migration_triggered = False
        
        self.controller_setup['first_controller'](time_now, sleep_time, K_VALUE)
        if self.migration_triggered:
            return
        
        self.controller_setup['second_controller'](time_now, sleep_time, K_VALUE)
        if self.migration_triggered:
            return
        
        self.controller_setup['third_controller'](time_now, sleep_time, K_VALUE)

    def imbalance_controller(self, time_now, sleep_time, k):
        imbalance_controller = controller_imbalance.Imbalance(self, PERCENTILE, THRESHOLD_IMBALANCE, MIN_IMPROVEMENT_IMBALANCE, THRESHOLD_OVERLOAD, NODE_CAPACITY)
        imbalance_controller.migrate_imbalance(time_now, sleep_time, k)

    
    def reactive_controller(self, time_now, sleep_time, K_VALUE):
        reactive_controller = controller_reactive.Reactive(self, THRESHOLD_OVERLOAD, THRESHOLD_UNDERLOAD, PERCENTILE, K_VALUE, M_VALUE)
        reactive_controller.migrate_reactive(time_now, sleep_time)
        
    def swap_controller(self, time_now, sleep_time, K_VALUE):
        swap_controller = controller_swap.Swap(self, THRESHOLD_OVERLOAD, THRESHOLD_UNDERLOAD, PERCENTILE, K_VALUE, M_VALUE)
        swap_controller.migrate_swap(time_now, sleep_time)

    def static_controller(self, time_now, sleep_time, K_VALUE):
        # DO NOTHING
        return
    