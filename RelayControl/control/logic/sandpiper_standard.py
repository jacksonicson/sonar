from logs import sonarlog
from model import types
import json
import controller
import numpy
import math
import util
import scoreboard
import placement
import migration_scheduler
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
FIRST_CONTROLLER = 'imbalance'
SECOND_CONTROLLER = 'reactive'
THIRD_CONTROLLER = 'swap'

######################

# Setup logging
logger = sonarlog.getLogger('controller')

class Sandpiper(controller.LoadBalancer):
    
    def __init__(self, pump, model):
        super(Sandpiper, self).__init__(pump, model, INTERVAL, START_WAIT)
        self.migration_scheduler = migration_scheduler.migration(self, K_VALUE)
        self.migration_triggered = False
        
        if FIRST_CONTROLLER == 'imbalance' or SECOND_CONTROLLER == 'imbalance' or THIRD_CONTROLLER == 'imbalance':
            self.imbalance_controller = True
        else:
            self.imbalance_controller = False
        if FIRST_CONTROLLER == 'reactive' or SECOND_CONTROLLER == 'reactive' or THIRD_CONTROLLER == 'reactive':    
            self.reactive_controller = True
        else:
            self.reactive_controller = False
        if FIRST_CONTROLLER == 'swap' or SECOND_CONTROLLER == 'swap' or THIRD_CONTROLLER == 'swap':
            self.swap_controller = True
        else:
            self.swap_controller = False
            
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
        
        if FIRST_CONTROLLER == 'imbalance':
            ############################################
            ## IMBALANCE MIGRATION #####################
            ############################################
            self.migrate_imbalance(time_now, sleep_time, K_VALUE)
            
            if self.migration_triggered:
                # if imbalance algorithm triggered migration, no further migrations will be executed
                return
        
        
        if self.reactive_controller or self.swap_controller:
            ############################################
            ## OVERLOAD/UNDERLOAD/SWAP MIGRATION #######
            ############################################
            # detect hotspots
            self.hotspot_detector()
                
            # calculate and sort nodes by their volume
            nodes = self.migration_manager()
            
            # trigger migration
            self.migration_trigger(nodes, sleep_time, time_now)
            
            if self.migration_triggered:
                # if overload/underload/swap triggered migration, no further migrations will be executed
                return
        
        if FIRST_CONTROLLER != 'imbalance' and self.imbalance_controller:
            ############################################
            ## IMBALANCE MIGRATION #####################
            ############################################
            self.migrate_imbalance(time_now, sleep_time, K_VALUE)
        
    def migrate_imbalance(self, time_now, sleep_time, k):
        # based on DSR algorithm
        
        # create snapshot of nodes and domains
        system_nodes = self.model.get_hosts(types.NODE)
        nodes = {}
        domains = {}
        migrations = {}
        for node in system_nodes:
            node_domains = {}
            
            for domain in node.domains.values():            
                new_domain = {}
                new_domain['name'] = domain.name
                new_domain['cpu'] = util.domain_to_server_cpu(node, domain, domain.percentile_load(PERCENTILE, k))
                new_domain['source'] = node.name
                node_domains[domain.name] = new_domain
                domains[domain.name] = new_domain
                
            new_node = {}
            new_node['name'] = node.name
            new_node['cpu'] = node.percentile_load(PERCENTILE, k)
            new_node['domains'] = node_domains
            new_node['normalized_cpu'] = self.normalized_cpu(new_node, k)
            nodes[node.name] = new_node
        
        # run load balancing    
        imbalance = self.imbalance(nodes, k)
        print 'IMBALANCE %s' % (imbalance)
        num_migrations = 0
        max_migrations = 10
        
        while (imbalance > THRESHOLD_IMBALANCE) and (num_migrations < max_migrations):
            best_migration = None
            best_improvement = 0
            
            for domain in domains.itervalues():
                # for every domain
                tmp_nodes = nodes
                
                # save parent node extra
                source = tmp_nodes[domain['source']]
                source_node = self.model.get_host(source['name'])
                
                if len(source['domains']) == 1:
                    # don't consider domains, which are alone on one node
                    continue
          
                for node in tmp_nodes.itervalues():
                    # consider every node as new parent for domain
                    
                    # calculate new cpu
                    target_node = self.model.get_host(node['name'])
                    target_domain = self.model.get_host(domain['name'])
                    node_cpu = node['cpu']
                    new_domain_cpu = util.domain_to_server_cpu(target_node, target_domain, target_domain.percentile_load(PERCENTILE, k))
                    old_domain_cpu = domain['cpu']
                    domain['cpu'] = new_domain_cpu
                    target_threshold = node_cpu + new_domain_cpu
                    
                    # don't migrate domain to same node nor empty node nor if overload threshold is exceeded
                    test = False
                    test |= target_node.name == source_node.name
                    test |= len(target_node.domains) == 0
                    test |= len(target_node.domains) >= 6
                    test |= target_threshold > THRESHOLD_OVERLOAD
                    test |= (time_now - target_node.blocked) <= sleep_time
                    test |= (time_now - source_node.blocked) <= sleep_time
                    
                    if test:
                        continue
                    
                    # migrate domain to node (in snapshot) and check new imbalance
                    node['domains'][domain['name']] = domain
                    del source['domains'][domain['name']]
                    old_normalized_cpu_node = node['normalized_cpu']
                    old_normalized_cpu_source = source['normalized_cpu']
                    node['normalized_cpu'] = self.normalized_cpu(node, k)
                    source['normalized_cpu'] = self.normalized_cpu(source, k)
                    new_imbalance = self.imbalance(tmp_nodes, k)
                    improvement = imbalance - new_imbalance
                    
                    if improvement > MIN_IMPROVEMENT_IMBALANCE and improvement > best_improvement:
                        best_migration = {'domain': target_domain.name, 'source': source_node.name, 'target': target_node.name}
                        best_source = source
                        best_target = node
                        best_domain = domain
                        best_improvement = improvement                    
                    
                    # go back to previous state
                    domain['cpu'] = old_domain_cpu
                    source['domains'][domain['name']] = domain
                    source['normalized_cpu'] = old_normalized_cpu_source
                    del node['domains'][domain['name']]
                    node['normalized_cpu'] = old_normalized_cpu_node
                                
            if best_migration is None:
                break
            
            # update imbalance and new nodes with best_migration
            imbalance -= best_improvement 
            migrations[num_migrations] = best_migration
            best_domain['source'] = best_target['name']
            best_target['domains'][best_domain['name']] = best_domain
            best_target['normalized_cpu'] = self.normalized_cpu(best_target, k)
            del best_source['domains'][best_domain['name']]
            best_source['normalized_cpu'] = self.normalized_cpu(best_source, k)
            num_migrations += 1
      
        # migrate domains that improve imbalance
        for migration in migrations.itervalues():
            domain = self.model.get_host(migration['domain'])
            source = self.model.get_host(migration['source'])
            target = self.model.get_host(migration['target'])
            
            self.migration_scheduler.add_migration(domain, source, target, 'Imbalance') 
            self.migration_triggered = True
            
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
                        if self.reactive_controller:
                            self.migrate_overload(node, nodes, source, domain, time_now, sleep_time, K_VALUE, False)
                        if self.swap_controller:
                            self.swap(node, nodes, source, domain, time_now, sleep_time, K_VALUE)
                        if self.reactive_controller:
                            self.migrate_overload(node, nodes, source, domain, time_now, sleep_time, K_VALUE, True)
                            
            except StopIteration: pass 
            
            if self.reactive_controller:
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
    
    def swap(self, node, nodes, source, domain, time_now, sleep_time, k):
        # Try all targets for swapping
        for target_node in reversed(range(nodes.index(node) + 1, len(nodes))):
            target_node = nodes[target_node]
            
            if len(target_node.domains) == 0:
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
                new_target_node_load = target_node.percentile_load(PERCENTILE, k) + util.domain_to_server_cpu(target_node, domain, domain.percentile_load(PERCENTILE, k))
                new_source_node_load = node.percentile_load(PERCENTILE, k) - util.domain_to_server_cpu(node, domain, domain.percentile_load(PERCENTILE, k))
              
                for target_domain in targets:
                    tmp_load = target_domain.percentile_load(PERCENTILE, k)
                    new_target_node_load -= util.domain_to_server_cpu(target_node, target_domain, tmp_load)
                    new_source_node_load += util.domain_to_server_cpu(node, target_domain, tmp_load)                              
                
                #Test if swap violates rules
                test = True
                test &= new_target_node_load < THRESHOLD_OVERLOAD
                test &= new_source_node_load < THRESHOLD_OVERLOAD     
                test &= len(node.domains) < 6
                test &= (time_now - target_node.blocked) > sleep_time
                test &= (time_now - source.blocked) > sleep_time
                
                if test:
                    self.migration_scheduler.add_migration(domain, source, target_node, 'Swap Part 1')
                    self.migration_triggered = True
                    for target_domain in targets:
                        self.migration_scheduler.add_migration(target_domain, target_node, source, 'Swap Part 2')
                    
                    raise StopIteration() 

    def volume(self, node, k):
        # Calculates volume for node and return node
        volume = 1.0 / max(0.001, float(100.0 - node.percentile_load(PERCENTILE, k)) / 100.0)
        node.volume = volume
        node.volume_size = volume / 8.0 # 8 GByte
        
        return node    
  
    def normalized_cpu(self, node, k):
        # Calculate normalized cpu of a node        
        load = 0
        for domain in node['domains'].itervalues():
            load += domain['cpu']
        
        return load / NODE_CAPACITY
            
                
    def imbalance(self, nodes, k):
        # Based on DRS     
        normalized_cpus = []
        for node in nodes.itervalues():
            if len(node['domains']) != 0:
                normalized_cpus.append(node['normalized_cpu'])

        return math.fabs(numpy.std(normalized_cpus))            
