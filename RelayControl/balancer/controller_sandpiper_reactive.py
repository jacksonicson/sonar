from logs import sonarlog
from balancer.model import types
from balancer import controller
import json
from virtual import nodes, placement

######################
## CONFIGURATION    ##
######################
START_WAIT = 120
INTERVAL = 300
THRESHOLD_OVERLOAD = 90
THRESHOLD_UNDERLOAD = 40
PERCENTILE = 80.0

K_VALUE = 20 # sliding windows size
M_VALUE = 17 # m values out of the window k must be above or below the threshold
######################

# Setup logging
logger = sonarlog.getLogger('controller')

class Controller(controller.LoadBalancer):
    
    def __init__(self, scoreboard, pump, model):
        super(Controller, self).__init__(scoreboard, pump, model, INTERVAL, START_WAIT)
        
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
            
        else:
            node_from.blocked = end_time
            node_to.blocked = end_time
        
        
    def balance(self):
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
            
            
        ############################################
        ## MIGRATION MANAGER #######################
        ############################################
        # Calculate volumes of each node
        nodes = []
        domains = []
        for node in self.model.get_hosts():
            volume = 1.0 / max(0.001, float(100.0 - node.percentile_load(PERCENTILE, k)) / 100.0)
            node.volume = volume
            node.volume_size = volume / 8.0 # 8 GByte
            
            if node.type == types.NODE:
                nodes.append(node)
            elif node.type == types.DOMAIN: 
                domains.append(node)
       
        # Sort nodes to their volume in DECREASING order
        # Multiplication with a big value to shift post comma digits to the front (integer)
        nodes.sort(lambda a, b: int((b.volume - a.volume) * 100000))
       
        
        ############################################
        ## MIGRATION TRIGGER #######################
        ############################################
        time_now = self.pump.sim_time()
        sleep_time = 60
        for node in nodes:
            node.dump()
            
            try:
                # Overload situation
                if node.overloaded:
                    # Source node to migrate from 
                    source = node
                    
                    # Sort domains by their VSR value in decreasing order 
                    node_domains = []
                    node_domains.extend(node.domains.values())
                    node_domains.sort(lambda a, b: int(b.volume_size - a.volume_size))
                    
                    # Try to migrate all domains by decreasing VSR value
                    for domain in node_domains:
                        
                        # Try all targets for the migration (reversed - starting at the BOTTOM)
                        for target in reversed(range(nodes.index(node) + 1, len(nodes))):
                            target = nodes[target]
                            
                            if len(target.domains) == 0:
                                # print 'skip %s - %s' % (target.name, target.domains)
                                continue
                             
                            domain_cpu_factor = target.cpu_cores / domain.cpu_cores
                             
                            test = True
                            test &= (target.percentile_load(PERCENTILE, k) + domain.percentile_load(PERCENTILE, k) / domain_cpu_factor) < THRESHOLD_OVERLOAD # Overload threshold
                            test &= len(target.domains) < 6
                            test &= (time_now - target.blocked) > sleep_time
                            test &= (time_now - source.blocked) > sleep_time
                            
                            if test: 
                                print 'Overload migration: %s from %s to %s' % (domain.name, source.name, target.name)
                                self.migrate(domain, source, target, K_VALUE)
                                raise StopIteration()
                            
                        for target in reversed(range(nodes.index(node) + 1, len(nodes))):
                            target = nodes[target]
                             
                            domain_cpu_factor = target.cpu_cores / domain.cpu_cores
                             
                            test = True
                            test &= (target.percentile_load(PERCENTILE, k) + domain.percentile_load(PERCENTILE, k) / domain_cpu_factor) < THRESHOLD_OVERLOAD # Overload threshold
                            test &= len(target.domains) < 6
                            test &= (time_now - target.blocked) > sleep_time
                            test &= (time_now - source.blocked) > sleep_time
                            
                            if test: 
                                print 'Overload migration (Empty): %s from %s to %s' % (domain.name, source.name, target.name)
                                self.migrate(domain, source, target, K_VALUE)
                                raise StopIteration()
                            
            except StopIteration: pass 
            
            try:
                # Underload  situation
                if node.underloaded:
                    # Source node to migrate from 
                    source = node
                    
                    # Sort domains by their VSR value in decreasing order 
                    node_domains = []
                    node_domains.extend(node.domains.values())
                    node_domains.sort(lambda a, b: int(b.volume_size - a.volume_size))
                    
                    # Try to migrate all domains by decreasing VSR value
                    for domain in node_domains:
                        
                        # Try all targets for the migration
                        for target in range(nodes.index(node) - 1):
                            target = nodes[target]
                            
                            if len(target.domains) == 0:
                                continue
                            
                            domain_cpu_factor = target.cpu_cores / domain.cpu_cores
                            
                            test = True
                            test &= (target.percentile_load(PERCENTILE, k) + domain.percentile_load(PERCENTILE, k) / domain_cpu_factor) < THRESHOLD_OVERLOAD # Overload threshold
                            test &= len(target.domains) < 6
                            test &= (time_now - target.blocked) > sleep_time
                            test &= (time_now - source.blocked) > sleep_time
                            
                            if test: 
                                print 'Underload migration: %s from %s to %s' % (domain.name, source.name, target.name)
                                self.migrate(domain, source, target, K_VALUE)                                    
                                raise StopIteration()
                        
                        
                        for target in range(nodes.index(node) - 1):
                            target = nodes[target]
                            
                            domain_cpu_factor = target.cpu_cores / domain.cpu_cores
                            
                            test = True
                            test &= (target.percentile_load(PERCENTILE, k) + domain.percentile_load(PERCENTILE, k) / domain_cpu_factor) < THRESHOLD_OVERLOAD # Overload threshold
                            test &= len(target.domains) < 6
                            test &= (time_now - target.blocked) > sleep_time
                            test &= (time_now - source.blocked) > sleep_time
                            
                            if test: 
                                print 'Underload migration (Empty): %s from %s to %s' % (domain.name, source.name, target.name)
                                self.migrate(domain, source, target, K_VALUE)                                    
                                raise StopIteration()
            except StopIteration: pass
