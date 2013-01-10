from logs import sonarlog
from model import types
import json
import controller
import util
import placement
import migration_scheduler
import controller_imbalance
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
# Notice: Swap cannot be executed before 'reactive'
CONTROLLER_SETTINGS = {
'first_controller' : 'swap',
'second_controller' : '',
'third_controller' : ''
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
        imbalance_controller.migrate_imbalance(time_now, sleep_time, k)(time_now, sleep_time, k)

    
    def reactive_controller(self, time_now, sleep_time, K_VALUE):
        # detect hotspots
        self.hotspot_detector()
            
        # calculate and sort nodes by their volume
        nodes = self.migration_manager()
        
        # trigger migration
        self.migration_trigger(nodes, sleep_time, time_now)
        
    def swap_controller(self, time_now, sleep_time, K_VALUE):
        swap_controller = controller_swap.Swap(self, THRESHOLD_OVERLOAD, THRESHOLD_UNDERLOAD, PERCENTILE, K_VALUE, M_VALUE)
        swap_controller.migrate_swap(time_now, sleep_time)

    def static_controller(self, time_now, sleep_time, K_VALUE):
        # DO NOTHING
        return
    
    def hotspot_detector(self):
        ############################################
        ## HOTSPOT DETECTOR ########################
        ############################################ 
        for node in self.model.get_hosts(types.NODE):
            # Check past readings
            readings = node.get_readings()
            
            # m out of the k last measurements are used to detect overloads 
            k = K_VALUE
            overload = 0
            underload = 0
            for reading in readings[-k:]:
                if reading > THRESHOLD_OVERLOAD: overload += 1
                if reading < THRESHOLD_UNDERLOAD: underload += 1

            m = M_VALUE   
            overload = (overload >= m)
            underload = (underload >= m)
             
            if overload:
                print 'Overload in %s - %s' % (node.name, readings[-k:])  
             
            # Update overload                                
            node.overloaded = overload
            node.underloaded = underload
          
    def migration_manager(self):
        ############################################
        ## MIGRATION MANAGER #######################
        ############################################
        # Calculate volumes of each node
        nodes = []
        domains = []
        for node in self.model.get_hosts():
            node = self.volume(node, K_VALUE)
            
            if node.type == types.NODE:
                nodes.append(node)
            elif node.type == types.DOMAIN: 
                domains.append(node)
       
        # Sort nodes to their volume in DECREASING order
        # Multiplication with a big value to shift post comma digits to the front (integer)
        nodes.sort(lambda a, b: int((b.volume - a.volume) * 100000))
        
        return nodes 
    
    def migration_trigger(self, nodes, sleep_time, time_now):
        ############################################
        ## MIGRATION TRIGGER #######################
        ############################################
        for node in nodes:
            node.dump()
            
            # Overload situation
            try:
                if node.overloaded:
                    # Source node to migrate from 
                    source = node
                    
                    # Sort domains by their VSR value in decreasing order 
                    node_domains = []
                    node_domains.extend(node.domains.values())
                    node_domains.sort(lambda a, b: int(b.volume_size - a.volume_size))
                    
                    # Try to migrate all domains by decreasing VSR value
                    for domain in node_domains:
                        self.migrate_overload(node, nodes, source, domain, time_now, sleep_time, K_VALUE, False)
                        self.migrate_overload(node, nodes, source, domain, time_now, sleep_time, K_VALUE, True)
                            
            except StopIteration: pass 
            
            # Underload situation
            try:
                if node.underloaded:
                    # Source node to migrate from 
                    source = node
                    
                    # Sort domains by their VSR value in decreasing order 
                    node_domains = []
                    node_domains.extend(node.domains.values())
                    node_domains.sort(lambda a, b: int(b.volume_size - a.volume_size))
                    
                    # Try to migrate all domains by decreasing VSR value
                    for domain in node_domains:
                        self.migrate_underload(node, nodes, source, domain, time_now, sleep_time, K_VALUE, False)
                        self.migrate_underload(node, nodes, source, domain, time_now, sleep_time, K_VALUE, True)
                            
            except StopIteration: pass
    
    def migrate_overload(self, node, nodes, source, domain, time_now, sleep_time, k, empty):
        # Try all targets for the migration (reversed - starting at the BOTTOM)
        for target in reversed(range(nodes.index(node) + 1, len(nodes))):
            target = nodes[target]
               
            if len(target.domains) == 0 and empty == False:
                continue
                             
            test = True
            test &= (target.percentile_load(PERCENTILE, k) + util.domain_to_server_cpu(target, domain, domain.percentile_load(PERCENTILE, k))) < THRESHOLD_OVERLOAD # Overload threshold
            test &= len(target.domains) < 6
            test &= (time_now - target.blocked) > sleep_time
            test &= (time_now - source.blocked) > sleep_time
                            
            if test: 
                migration_type = 'Overload (Empty=%s)' % (empty)
                self.migration_scheduler.add_migration(domain, source, target, migration_type) 
                self.migration_triggered = True
                raise StopIteration()
        
    def migrate_underload(self, node, nodes, source, domain, time_now, sleep_time, k, empty):
        # Try all targets for the migration
        for target in range(nodes.index(node) - 1):
            target = nodes[target]
            
            if len(target.domains) == 0 and empty == False:
                continue
            
            test = True
            test &= (target.percentile_load(PERCENTILE, k) + util.domain_to_server_cpu(target, domain, domain.percentile_load(PERCENTILE, k))) < THRESHOLD_OVERLOAD # Overload threshold
            test &= len(target.domains) < 6
            test &= (time_now - target.blocked) > sleep_time
            test &= (time_now - source.blocked) > sleep_time
            
            if test: 
                migration_type = 'Underload (Empty=%s)' % (empty)
                self.migration_scheduler.add_migration(domain, source, target, migration_type)                          
                self.migration_triggered = True
                raise StopIteration()

    def volume(self, node, k):
        # Calculates volume for node and return node
        volume = 1.0 / max(0.001, float(100.0 - node.percentile_load(PERCENTILE, k)) / 100.0)
        node.volume = volume
        node.volume_size = volume / 8.0 # 8 GByte
        
        return node    
            