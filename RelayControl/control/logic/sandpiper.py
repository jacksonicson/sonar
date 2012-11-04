from logs import sonarlog
from model import types
import json
import logic
import time

######################
## CONFIGURATION    ##
######################
START_WAIT = 60
INTERVAL = 60 * 5
THRESHOLD_OVERLOAD = 90
THRESHOLD_UNDERLOAD = 40
PERCENTILE = 80.0

K_VALUE = 20 # sliding windows size
M_VALUE = 17 # m values out of the window k must be above or below the threshold
######################

# Setup logging
logger = sonarlog.getLogger('controller')

class Sandpiper(logic.LoadBalancer):
    
    def __init__(self, model, production):
        super(Sandpiper, self).__init__(model, production, INTERVAL)
        
        
    def dump(self):
        logger.info('Controller: Sandpiper')
        logger.info('START_WAIT = %i' % START_WAIT)
        logger.info('INTERVAL = %i' % INTERVAL)
        logger.info('THRESHOLD_OVERLOAD = %i' % THRESHOLD_OVERLOAD)
        logger.info('THRESHOLD_UNDERLOAD = %i' % THRESHOLD_UNDERLOAD)
        logger.info('_PERCENTILE = %i' % PERCENTILE)
        logger.info('K_VALUE = %i' % K_VALUE)
        logger.info('M_VALUE = %i' % M_VALUE)
    
    def forecast(self, data):
        # TODO double exponential smoothing (holt winter)
        import statsmodels.api as sm
        import statsmodels as sm2

        model = sm2.tsa.ar_model.AR(data).fit()
        try:
            value = model.predict(len(data), len(data) + 1)
            return value[0]
        except:
            return data[-1]
        
        
    def post_migrate_hook(self, success, domain, node_from, node_to):
        if success:
            # Release block
            time_now = time.time()
            node_from.blocked = time_now
            node_to.blocked = time_now
            
            # Reset CPU consumption: Necessary because the old CPU readings
            # may trigger another migrations as they do not represent the load
            # without the VM
            node_from.flush(50)
            node_to.flush(50)
            
        else:
            
            time_now = time.time()
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
        
        
    def lb(self):
        ############################################
        ## HOTSPOT DETECTOR ########################
        ############################################
        
        sum_readings = 0
        counter = 0
        min_value = 100
        for node in self.model.get_hosts(types.NODE):
            counter += 1
            readings = node.get_readings()
            
            # only sum the latest reading and get value of least loaded node
            for reading in readings[-1:]:
                sum_readings += reading
                # TODO if node name is unique, better save node name
                if reading < min_value: min_value = reading
            
        avg_reading = sum_readings / counter;
        
        for node in self.model.get_hosts(types.NODE):
            # Check past readings
            readings = node.get_readings()
            
            # m out of the k last measurements are used to detect overloads 
            k = K_VALUE
            overload = 0
            underload = 0
            for reading in readings[-k:]:
                if reading > THRESHOLD_OVERLOAD: overload += 1
                if reading == min_value: underload += 1

            m = M_VALUE
            overload = (overload >= m)
            underload = (underload != 0) and (avg_reading < THRESHOLD_UNDERLOAD)
             
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
        time_now = time.time()
        sleep_time = 10
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
                             
                            test = True
                            test &= (target.percentile_load(PERCENTILE, k) + (domain.percentile_load(PERCENTILE, k) / 2.0)) < THRESHOLD_OVERLOAD # Overload threshold
                            test &= len(target.domains) < 6
                            test &= (time_now - target.blocked) > sleep_time
                            test &= (time_now - source.blocked) > sleep_time
                            
                            if test: 
                                print 'Overload migration: %s from %s to %s' % (domain.name, source.name, target.name)
                                self.migrate(domain, source, target, K_VALUE)
                                raise StopIteration()
                            
                        for target in reversed(range(nodes.index(node) + 1, len(nodes))):
                            target = nodes[target]
                             
                            test = True
                            test &= (target.percentile_load(PERCENTILE, k) + (domain.percentile_load(PERCENTILE, k) / 2.0)) < THRESHOLD_OVERLOAD # Overload threshold
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
                            
                            test = True
                            test &= (target.percentile_load(PERCENTILE, k) + (domain.percentile_load(PERCENTILE, k) / 2.0)) < THRESHOLD_OVERLOAD # Overload threshold
                            test &= len(target.domains) < 6
                            test &= (time_now - target.blocked) > sleep_time
                            test &= (time_now - source.blocked) > sleep_time
                            
                            if test: 
                                print 'Underload migration: %s from %s to %s' % (domain.name, source.name, target.name)
                                self.migrate(domain, source, target, K_VALUE)                                    
                                raise StopIteration()
                        
                        
                        for target in range(nodes.index(node) - 1):
                            target = nodes[target]
                            
                            test = True
                            test &= (target.percentile_load(PERCENTILE, k) + (domain.percentile_load(PERCENTILE, k) / 2.0)) < THRESHOLD_OVERLOAD # Overload threshold
                            test &= len(target.domains) < 6
                            test &= (time_now - target.blocked) > sleep_time
                            test &= (time_now - source.blocked) > sleep_time
                            
                            if test: 
                                print 'Underload migration (Empty): %s from %s to %s' % (domain.name, source.name, target.name)
                                self.migrate(domain, source, target, K_VALUE)                                    
                                raise StopIteration()
            except StopIteration: pass
        
            
        ############################################
        ## SWAP TRIGGER ############################
        ############################################
        
        time_now = time.time()
        sleep_time = 10
        for node in nodes:
            node.dump()
            
            try:
                #Overload situation
                if node.overloaded:
                    # Source node to swap from
                    source =node
                    
                    # Sort domains by their VSR value in decreasing order
                    node_domains = []
                    node_domains.extend(node.domains.values())
                    node_domains.sort(lambda a, b: int(b.volume_size - a.volume_size))
                    
                    # Try to swap all domains by decreasing VSR value
                    for domain in node_domains:
                        
                        # Try all targets for swapping
                        for target_node in reversed(range(nodes.index(node) + 1, len(nodes))):
                            target_node = nodes[target_node]
                            
                            # Sort domains of target by their VSR value in ascending order
                            target_domains = []
                            target_domains.extend(target_node.domains.values())
                            target_domains.sort(lambda a, b: int(b.volume_size - a.volume_size), reverse=True)
                            
                            # Try to find TWO nodes for swapping
                            for target in range(0, len(target_domains)-2):
                                target_one = target_domains[target]
                                target_two = target_domains[target+1]
                                
                                test = True
                                # TODO correct test
                                test &= (target_node.percentile_load(PERCENTILE, k) - target_one.percentile_load(PERCENTILE, k) - target_two.percentile_load(PERCENTILE, k) + domain.percentile_load(PERCENTILE, k)) < THRESHOLD_OVERLOAD
                                test &= (node.percentile_load(PERCENTILE, k) - domain.percentile_load(PERCENTILE, k) + target_one.percentile_load(PERCENTILE, k) + target_two.percentile_load(PERCENTILE, k)) < THRESHOLD_OVERLOAD
                                test &= len(node.domains) < 6
                                test &= (time_now - target_node.blocked) > sleep_time
                                test &= (time_now - source.blocked) > sleep_time
                                
                                if test:
                                    print 'Overload swap: %s from %s swapped with %s and %s from %s' % (domain.name, source.name, target_one.name, target_two.name, target_node.name)
                                    self.migrate(domain, source, target_node, K_VALUE)
                                    self.migrate(target_one, target_node, source, K_VALUE)
                                    self.migrate(target_two, target_node, source, K_VALUE)
                                    raise StopIteration()
                                    raise StopIteration()
                
            except StopIteration: pass
        
        
