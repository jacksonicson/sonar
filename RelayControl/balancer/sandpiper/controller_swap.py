from balancer.model import types
import configuration_advanced
from virtual import nodes

class Swap():
    
    def __init__(self, model, migration_scheduler):
        self.model = model
        self.migration_scheduler = migration_scheduler
        
        self.THRESHOLD_OVERLOAD = configuration_advanced.THRESHOLD_OVERLOAD
        self.THRESHOLD_UNDERLOAD = configuration_advanced.THRESHOLD_UNDERLOAD
        self.PERCENTILE = configuration_advanced.PERCENTILE
        self.K_VALUE = configuration_advanced.K_VALUE
        self.M_VALUE = configuration_advanced.M_VALUE
        
    def migrate_swap(self, time_now, sleep_time):
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
                        
                        # Try all targets for swapping
                        for target_node in reversed(range(nodes.index(node) + 1, len(nodes))):
                            target_node = nodes[target_node]
                            
                            if len(target_node.domains) == 0:
                                continue
                            
                            # Sort domains of target by their VSR value in ascending order
                            target_domains = []
                            target_domains.extend(target_node.domains.values())
                            target_domains.sort(lambda a, b: int((a.volume_size - b.volume_size)))
                            
                            # Try to find one or more low VSR VMs for swapping
                            for target in range(0, len(target_domains)):
                                targets = []
                                
                                # Get one or more VMs
                                for i in range(0, target+1):
                                    targets.append(target_domains[i])                
                
                                # Calculate new loads
                                new_target_node_load = target_node.percentile_load(self.PERCENTILE, k) + nodes.domain_to_server_cpu(target_node, domain, domain.percentile_load(self.PERCENTILE, k))
                                new_source_node_load = node.percentile_load(self.PERCENTILE, k) - nodes.domain_to_server_cpu(node, domain, domain.percentile_load(self.PERCENTILE, k))
                              
                                for target_domain in targets:
                                    tmp_load = target_domain.percentile_load(self.PERCENTILE, k)
                                    new_target_node_load -= nodes.domain_to_server_cpu(target_node, target_domain, tmp_load)
                                    new_source_node_load += nodes.domain_to_server_cpu(node, target_domain, tmp_load)                              
                                
                                #Test if swap violates rules
                                test = True
                                test &= new_target_node_load < self.THRESHOLD_OVERLOAD
                                test &= new_source_node_load < self.THRESHOLD_OVERLOAD 
                                test &= len(node.domains) < 6
                                test &= (time_now - target_node.blocked) > sleep_time
                                test &= (time_now - source.blocked) > sleep_time
                                
                                if test:
                                    self.migration_scheduler.add_migration(domain, source, target_node, 'Swap Part 1')
                                    for target_domain in targets:
                                        self.migration_scheduler.add_migration(target_domain, target_node, source, 'Swap Part 2')
                                    
                                    raise StopIteration() 
                            
            except StopIteration: 
                migration_triggered = True
                pass 
        
        return migration_triggered