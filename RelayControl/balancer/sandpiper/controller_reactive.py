from balancer.model import types
from virtual import nodes

class Reactive():
    
    def __init__(self, controller, threshold_overload, threshold_underload, percentile, k_value, m_value):
        self.controller = controller
        
        global THRESHOLD_OVERLOAD 
        THRESHOLD_OVERLOAD = threshold_overload
                
        global THRESHOLD_UNDERLOAD
        THRESHOLD_UNDERLOAD = threshold_underload
        
        global PERCENTILE 
        PERCENTILE = percentile
        
        global K_VALUE
        K_VALUE = k_value
        
        global M_VALUE
        M_VALUE = m_value
        
    def migrate_reactive(self, time_now, sleep_time):
        ############################################
        ## HOTSPOT DETECTOR ########################
        ############################################
        for node in self.controller.model.get_hosts(types.NODE):
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
        for node in self.controller.model.get_hosts():
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
                        self.migrate_overload(node, nodes, source, domain, time_now, sleep_time, K_VALUE, False)
                        self.migrate_overload(node, nodes, source, domain, time_now, sleep_time, K_VALUE, True)
                            
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
            test &= (target.percentile_load(PERCENTILE, k) + nodes.domain_to_server_cpu(target, domain, domain.percentile_load(PERCENTILE, k))) < THRESHOLD_OVERLOAD # Overload threshold
            test &= len(target.domains) < 6
            test &= (time_now - target.blocked) > sleep_time
            test &= (time_now - source.blocked) > sleep_time
                            
            if test: 
                migration_type = 'Overload (Empty=%s)' % (empty)
                self.controller.migration_scheduler.add_migration(domain, source, target, migration_type) 
                self.controller.migration_triggered = True
                raise StopIteration()
        
    def migrate_underload(self, node, nodes, source, domain, time_now, sleep_time, k, empty):
        # Try all targets for the migration
        for target in range(nodes.index(node) - 1):
            target = nodes[target]
            
            if len(target.domains) == 0 and empty == False:
                continue
            
            test = True
            test &= (target.percentile_load(PERCENTILE, k) + nodes.domain_to_server_cpu(target, domain, domain.percentile_load(PERCENTILE, k))) < THRESHOLD_OVERLOAD # Overload threshold
            test &= len(target.domains) < 6
            test &= (time_now - target.blocked) > sleep_time
            test &= (time_now - source.blocked) > sleep_time
            
            if test: 
                migration_type = 'Underload (Empty=%s)' % (empty)
                self.controller.migration_scheduler.add_migration(domain, source, target, migration_type)                          
                self.controller.migration_triggered = True
                raise StopIteration()
