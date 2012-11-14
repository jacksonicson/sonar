from logs import sonarlog
from model import types
import json
import logic
import time
import numpy

######################
## CONFIGURATION    ##
######################
START_WAIT = 0
INTERVAL = 20
THRESHOLD_OVERLOAD = 90
THRESHOLD_UNDERLOAD = 40
PERCENTILE = 80.0

K_VALUE = 20 # sliding windows size
M_VALUE = 17 # m values out of the window k must be above or below the threshold
######################

# Setup logging
logger = sonarlog.getLogger('controller')

class Sandpiper_standard(logic.LoadBalancer):
    
    def __init__(self, model, production):
        super(Sandpiper_standard, self).__init__(model, production, INTERVAL)
        
        
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
            value = model.predict(len(data) - 1, len(data))
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
            forecast = self.forecast(readings[-k:])        
            overloaded = True
            overloaded &= (overload >= m)
            overloaded &= (forecast > THRESHOLD_OVERLOAD)
        
            underloaded = True
            underloaded &= (underload >= m)
            underloaded &= (forecast < THRESHOLD_UNDERLOAD)
             
            if overloaded:
                print 'Overload in %s - %s' % (node.name, readings[-k:])  
             
            # Update overload                                
            node.overloaded = overloaded
            node.underloaded = underloaded
            
            
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
                        self.migrate_overload(node, nodes, source, domain, time_now, sleep_time, k, False)
                        self.swap(node, nodes, source, domain, time_now, sleep_time, k)
                        self.migrate_overload(node, nodes, source, domain, time_now, sleep_time, k, True)
                            
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
                        self.migrate_underload(node, nodes, source, domain, time_now, sleep_time, k, False)
                        self.migrate_underload(node, nodes, source, domain, time_now, sleep_time, k, True)
                        
            except StopIteration: pass


    def migrate_overload(self, node, nodes, source, domain, time_now, sleep_time, k, empty):
        # Try all targets for the migration (reversed - starting at the BOTTOM)
        for target in reversed(range(nodes.index(node) + 1, len(nodes))):
            target = nodes[target]
                            
            if len(target.domains) == 0 and empty == False:
                # print 'skip %s - %s' % (target.name, target.domains)
                continue
                             
            test = True
            test &= (target.percentile_load(PERCENTILE, k) + self.domain_to_server_cpu(target, domain, domain.percentile_load(PERCENTILE, k))) < THRESHOLD_OVERLOAD # Overload threshold
            test &= len(target.domains) < 6
            test &= (time_now - target.blocked) > sleep_time
            test &= (time_now - source.blocked) > sleep_time
                            
            if test: 
                print ' --------------- Overload migration (Empty = %s): %s from %s to %s' % (empty, domain.name, source.name, target.name)
                self.migrate(domain, source, target, K_VALUE)
                raise StopIteration()
        
        
    def swap(self, node, nodes, source, domain, time_now, sleep_time, k):
        # Try all targets for swapping
        for target_node in reversed(range(nodes.index(node) + 1, len(nodes))):
            target_node = nodes[target_node]
            
            if len(target_node.domains) == 0:
                # print 'skip %s - %s' % (target.name, target.domains)
                continue
            
            # Sort domains of target by their VSR value in ascending order
            target_domains = []
            target_domains.extend(target_node.domains.values())
            target_domains.sort(lambda a, b: int((a.volume_size - b.volume_size) * 100000))
            
            # Try to find one or more low VSR VMs for swapping
            for target in range(0, len(target_domains)):
                targets = []
                
                # Get one or more VMs
                for i in range(0, target+1):
                    targets.append(target_domains[i])                

                # Calculate new loads
                new_target_node_load = target_node.percentile_load(PERCENTILE, k) + self.domain_to_server_cpu(target_node, domain, domain.percentile_load(PERCENTILE, k))
                new_source_node_load = node.percentile_load(PERCENTILE, k) - self.domain_to_server_cpu(node, domain, domain.percentile_load(PERCENTILE, k))
                #print 'Target Node: Name: %s ;Load: %s' % (target_node.name, target_node.percentile_load(PERCENTILE, k))
                #print 'Source Node: Name: %s ;Load: %s' % (node.name, node.percentile_load(PERCENTILE, k))
                #print 'Source VM: Name: %s ;Load: %s' % (domain.name, self.domain_to_server_cpu(node, domain, domain.percentile_load(PERCENTILE, k)))
                for target_domain in targets:
                    tmp_load = target_domain.percentile_load(PERCENTILE, k)
                    #print 'Target Node: Name: %s ;Load on Target: %s' % (target_domain.name, self.domain_to_server_cpu(target_node, target_domain, tmp_load))
                    #print 'Target Node: Name: %s ;Load on Source: %s' % (target_domain.name, self.domain_to_server_cpu(node, target_domain, tmp_load) )
                    new_target_node_load -= self.domain_to_server_cpu(target_node, target_domain, tmp_load)
                    new_source_node_load += self.domain_to_server_cpu(node, target_domain, tmp_load)                              
                
                #Test if swap violates rules
                test = True
                #print ' --------------- Source Load: %s ; Target Load: %s' % (new_source_node_load, new_target_node_load)
                test &= new_target_node_load < THRESHOLD_OVERLOAD
                test &= new_source_node_load < THRESHOLD_OVERLOAD     
                test &= len(node.domains) < 6
                test &= (time_now - target_node.blocked) > sleep_time
                test &= (time_now - source.blocked) > sleep_time
                
                if test:
                    output = ' --------------- Overload swap: ' + domain.name + ' from ' + source.name + ' swapped with '
                    for target_domain in targets:
                        #TODO remove comma for last elem
                        output += target_domain.name + ', '
                    output += 'from ' + target_node.name
                    print '%s' % (output)
                    
                    self.migrate(domain, source, target_node, K_VALUE)
                    
                    for target_domain in targets:
                        self.migrate(target_domain, target_node, source, K_VALUE)
                        
                    raise StopIteration() 


    def migrate_underload(self, node, nodes, source, domain, time_now, sleep_time, k, empty):
        # Try all targets for the migration
        for target in range(nodes.index(node) - 1):
            target = nodes[target]
            
            if len(target.domains) == 0 and empty == False:
                continue
            
            test = True
            test &= (target.percentile_load(PERCENTILE, k) + self.domain_to_server_cpu(target, domain, domain.percentile_load(PERCENTILE, k))) < THRESHOLD_OVERLOAD # Overload threshold
            test &= len(target.domains) < 6
            test &= (time_now - target.blocked) > sleep_time
            test &= (time_now - source.blocked) > sleep_time
            
            if test: 
                print ' --------------- Underload migration (Empty = %s): %s from %s to %s' % (empty, domain.name, source.name, target.name)
                self.migrate(domain, source, target, K_VALUE)                                    
                raise StopIteration()
            
            
    def normalized_entitlement(self, node, domains, k):
        # Based on DRS, but use of precentile load as entitlement
        sum_entitlement = 0
        for domain in domains:
            sum_entitlement += domain.percentile_load(PERCENTILE, k)
          
        return sum_entitlement / node.percentile_load(PERCENTILE, k)    
                
                
    def imbalance(self, nodes, k):
        # Based on DRS
        normalized_entitlements = []
        for node in nodes:
            normalized_entitlements.append(self.normalized_entitlement(node, node.domains, k))
        
        return numpy.std(normalized_entitlements) 