from analytics import dexp_smooth as smoother
from logs import sonarlog
from model import types
import configuration
import controller
import json
import numpy as np

######################
## CONFIGURATION    ##
######################
if configuration.PRODUCTION: 
    START_WAIT = 120
    INTERVAL = 20
    THRESHOLD_OVERLOAD = 90
    THRESHOLD_UNDERLOAD = 30
    PERCENTILE = 80.0
    
#    K_VALUE = 100 # sliding windows size
#    M_VALUE = 99 # m values out of the window k must be above or below the threshold
    
else:
    
    START_WAIT = 10 * 60
    INTERVAL = 5 * 60
    THRESHOLD_OVERLOAD = 90
    THRESHOLD_UNDERLOAD = 40
    PERCENTILE = 80.0
    
    # This is equal to an percentile
    # K_VALUE = 100 
    # M_VALUE = 97
    THR_PERCENTILE = 0.2 # 0.2

######################

# Setup logging
logger = sonarlog.getLogger('controller')

class Sandpiper(controller.LoadBalancer):
    
    def __init__(self, pump, model):
        super(Sandpiper, self).__init__(pump, model, INTERVAL)
        self.var = []
        
    def dump(self):
        print 'Dump Sandpiper controller configuration...'
        logger.info('Controller Configuration: %s' % json.dumps({'name' : 'Sandpiper',
                                                                 'start_wait' : START_WAIT,
                                                                 'interval' : INTERVAL,
                                                                 'threshold_overload' : THRESHOLD_OVERLOAD,
                                                                 'threshold_underload' : THRESHOLD_UNDERLOAD,
                                                                 'percentile' : PERCENTILE,
                                                                 'thr_percentile' : THR_PERCENTILE,
                                                                 }))
    
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
            print self.var
        else:
            node_from.blocked = end_time
            node_to.blocked = end_time
        
        
    
    def lb(self):
        ############################################
        ## HOTSPOT DETECTOR ########################
        ############################################
        k = 100
        for node in self.model.get_hosts(types.NODE):
            # Check past readings
            readings = node.get_readings()
            
            # Calculate percentile on the data
            slc = readings[-k:]
            
            forecast = smoother.single_exponential_smoother(slc)[0]
            forecast = np.mean(slc)
            forecast = smoother.double_exponential_smoother(slc)[0]
            forecast = smoother.ar_forecast(slc)
            
            percentile = np.percentile(slc, THR_PERCENTILE)
            percentile_ = np.percentile(slc, 1 - THR_PERCENTILE)
            
            overload = (percentile > THRESHOLD_OVERLOAD)
            underload = (percentile_ < THRESHOLD_UNDERLOAD)
            overload = (overload and forecast > THRESHOLD_OVERLOAD)
            underload = (underload and forecast < THRESHOLD_UNDERLOAD)
             
            if overload:
                print 'Overload in %s - %s' % (node.name, slc)  
             
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
                                self.migrate(domain, source, target, k)
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
                                self.migrate(domain, source, target, k)
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
                                self.migrate(domain, source, target, k)                                    
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
                                self.migrate(domain, source, target, k)                                    
                                raise StopIteration()
            except StopIteration: pass
