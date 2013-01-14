from balancer.model import types
import configuration_advanced
from virtual import nodes as nodesv

class Reactive():
    
    def __init__(self, model, migration_scheduler):
        self.model = model
        self.migration_scheduler = migration_scheduler
        
        self.THRESHOLD_OVERLOAD = configuration_advanced.THRESHOLD_OVERLOAD
        self.THRESHOLD_UNDERLOAD = configuration_advanced.THRESHOLD_UNDERLOAD
        self.PERCENTILE = configuration_advanced.PERCENTILE
        self.K_VALUE = configuration_advanced.K_VALUE
        self.M_VALUE = configuration_advanced.M_VALUE
        
    def migrate_reactive(self, time_now, sleep_time):
        ############################################
        ## HOTSPOT DETECTOR ########################
        ############################################
        for node in self.model.get_hosts(types.NODE):
            # Check past readings
            readings = node.get_readings()
            
            # m out of the k last measurements are used to detect overloads 
            k = self.K_VALUE
            overload = 0
            underload = 0
            for reading in readings[-k:]:
                if reading > self.THRESHOLD_OVERLOAD: overload += 1
                if reading < self.THRESHOLD_UNDERLOAD: underload += 1

            m = self.M_VALUE
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
            volume = 1.0 / max(0.001, float(100.0 - node.percentile_load(self.PERCENTILE, k)) / 100.0)
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
        migration_triggered = False
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
                        self.migrate_overload(node, nodes, source, domain, time_now, sleep_time, False)
                        self.migrate_overload(node, nodes, source, domain, time_now, sleep_time, True)
                            
            except StopIteration: 
                migration_triggered = True
                pass 
            
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
                        self.migrate_underload(node, nodes, source, domain, time_now, sleep_time, False)
                        self.migrate_underload(node, nodes, source, domain, time_now, sleep_time, True)
                       
            except StopIteration: 
                migration_triggered = True
                pass
        
        return migration_triggered
  
    def migrate_overload(self, node, nodes, source, domain, time_now, sleep_time, empty):
        # Try all targets for the migration (reversed - starting at the BOTTOM)
        for target in reversed(range(nodes.index(node) + 1, len(nodes))):
            target = nodes[target]
               
            if len(target.domains) == 0 and empty == False:
                continue
                             
            test = True
            test &= (target.percentile_load(self.PERCENTILE, self.K_VALUE) + nodesv.to_node_load(domain.percentile_load(self.PERCENTILE, self.K_VALUE))) < self.THRESHOLD_OVERLOAD # Overload threshold
            test &= len(target.domains) < 6
            test &= (time_now - target.blocked) > sleep_time
            test &= (time_now - source.blocked) > sleep_time
                            
            if test: 
                migration_type = 'Overload (Empty=%s)' % (empty)
                self.migration_scheduler.add_migration(domain, source, target, migration_type) 
                raise StopIteration()
        
    def migrate_underload(self, node, nodes, source, domain, time_now, sleep_time, empty):
        # Try all targets for the migration
        for target in range(nodes.index(node) - 1):
            target = nodes[target]
            
            if len(target.domains) == 0 and empty == False:
                continue
            
            test = True
            test &= (target.percentile_load(self.PERCENTILE, self.K_VALUE) + nodesv.to_node_load(domain.percentile_load(self.PERCENTILE, self.K_VALUE))) < self.THRESHOLD_OVERLOAD # Overload threshold
            test &= len(target.domains) < 6
            test &= (time_now - target.blocked) > sleep_time
            test &= (time_now - source.blocked) > sleep_time
            
            if test: 
                migration_type = 'Underload (Empty=%s)' % (empty)
                self.migration_scheduler.add_migration(domain, source, target, migration_type)                          
                raise StopIteration()
