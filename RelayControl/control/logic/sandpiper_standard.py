from logs import sonarlog
from model import types
import json
import controller
import time
import numpy
import math

######################
## CONFIGURATION    ##
######################
START_WAIT = 0
INTERVAL = 20
THRESHOLD_OVERLOAD = 90
THRESHOLD_UNDERLOAD = 40
PERCENTILE = 80.0
THRESHOLD_IMBALANCE = 0.04
MIN_IMPROVEMENT_IMBALANCE = 0.005

K_VALUE = 20 # sliding windows size
M_VALUE = 17 # m values out of the window k must be above or below the threshold
######################

# Setup logging
logger = sonarlog.getLogger('controller')

# Migration Queue
migration_queue = []

class Sandpiper(controller.LoadBalancer):
    
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
            node = self.volume(node, k)
            
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
                    node_domains.sort(lambda a, b: int((b.volume_size - a.volume_size) * 100000))
                    
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
                    node_domains.sort(lambda a, b: int((b.volume_size - a.volume_size) * 100000))
                    
                    # Try to migrate all domains by decreasing VSR value
                    for domain in node_domains:
                        self.migrate_underload(node, nodes, source, domain, time_now, sleep_time, k, False)
                        self.migrate_underload(node, nodes, source, domain, time_now, sleep_time, k, True)
                        
            except StopIteration: pass
        
        self.migrate_overload_imbalance(time_now, sleep_time, k)
        self.migration_scheduler()

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
                source_load = source.percentile_load(PERCENTILE, k)
                target_load = target.percentile_load(PERCENTILE, k)
                domain_load = self.domain_to_server_cpu(target, domain, domain.percentile_load(PERCENTILE, k))
                print 'source load: %s; target load: %s; domain_load: %s' % (source_load, target_load, domain_load)
                #self.migrate(domain, source, target, K_VALUE)
                part = self.migration_part(domain, source, target, 'Overload', k) 
                migration = []
                migration.append(part)
                migration_queue.append(migration)    
                raise StopIteration()

    def migrate_overload_imbalance(self, time_now, sleep_time, k):
        # Based on DSR algorithm
        
        system_nodes = self.model.get_hosts(types.NODE)

        # create snapshot of nodes and domains
        nodes = {}
        domains = {}
        migrations = {}
        for node in system_nodes:
            node_domains = {}
            
            for domain in node.domains.values():            
                new_domain = {}
                new_domain['name'] = domain.name
                new_domain['volume'] = self.volume(domain, k).volume
                new_domain['source'] = node.name
                node_domains[domain.name] = new_domain
                domains[domain.name] = new_domain
                
            new_node = {}
            new_node['name'] = node.name
            new_node['volume'] = self.volume(node, k).volume
            new_node['domains'] = node_domains
            nodes[node.name] = new_node
        
            
        imbalance = self.imbalance(nodes, k)
        print 'imbalance before: %s' % (imbalance)
        num_migrations = 0
        max_migrations = 10
        
        while (imbalance > THRESHOLD_IMBALANCE) and (num_migrations < max_migrations):
            best_migration = None
            best_improvement = 0
            
            for domain in domains.itervalues():
                # for every domain
                tmp_nodes = nodes

                for node in tmp_nodes.itervalues():
                    # remove domain from parent node and save node extra
                    if domain['name'] in node['domains']:
                        del node['domains'][domain['name']]
                        source = node
                
                for node in tmp_nodes.itervalues():
                    
                    if node['name'] == source['name'] or len(node['domains']) == 0:
                        # cannot migrate to same node and don't consider empty servers
                        continue

                    # migrate domain to node and check new imbalance
                    node['domains'][domain['name']] = domain
                    new_imbalance = self.imbalance(tmp_nodes, k)
                    improvement = imbalance - new_imbalance
                    
                    if improvement > MIN_IMPROVEMENT_IMBALANCE:
                        if improvement > best_improvement:
                            best_migration = {'domain': domain['name'], 'source': source['name'], 'target': node['name']}
                            best_improvement = improvement
                        else:
                            # go back to previous state
                            source['domains'][domain['name']] = domain
                            del node['domains'][domain['name']]
                    else:
                        # go back to previous state
                        source['domains'][domain['name']] = domain
                        del node['domains'][domain['name']]
                                                
            if best_migration is None:
                break
            
            # update imbalance and new nodes
            imbalance -= best_improvement 
            migrations[num_migrations] = best_migration
            num_migrations += 1
            print 'best improvement in this loop: %s; imbalance after: %s; domain: %s; source: %s; target: %s' % (best_improvement, imbalance, best_migration['domain'], best_migration['source'], best_migration['target'])

        
        # migrate domains that improve imbalance
        for migration in migrations.itervalues():
            domain = self.model.get_host(migration['domain'])
            source = self.model.get_host(migration['source'])
            target = self.model.get_host(migration['target'])
            
            test = True
            test &= len(target.domains) < 6
            test &= (time_now - target.blocked) > sleep_time
            test &= (time_now - source.blocked) > sleep_time
                            
            if test: 
                #self.migrate(domain, source, target, K_VALUE)
                part = self.migration_part(domain, source, target, 'Imbalance', k) 
                migration = []
                migration.append(part)
                migration_queue.append(migration)    
        
        
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
                new_target_node_load = target_node.percentile_load(PERCENTILE, k) + self.domain_to_server_cpu(target_node, domain, domain.percentile_load(PERCENTILE, k))
                new_source_node_load = node.percentile_load(PERCENTILE, k) - self.domain_to_server_cpu(node, domain, domain.percentile_load(PERCENTILE, k))
              
                for target_domain in targets:
                    tmp_load = target_domain.percentile_load(PERCENTILE, k)
                    new_target_node_load -= self.domain_to_server_cpu(target_node, target_domain, tmp_load)
                    new_source_node_load += self.domain_to_server_cpu(node, target_domain, tmp_load)                              
                

                #Test if swap violates rules
                test = True
                test &= new_target_node_load < THRESHOLD_OVERLOAD
                test &= new_source_node_load < THRESHOLD_OVERLOAD     
                test &= len(node.domains) < 6
                test &= (time_now - target_node.blocked) > sleep_time
                test &= (time_now - source.blocked) > sleep_time
                
                if test:
                    #self.migrate(domain, source, target_node, K_VALUE)
                    migration_part = self.migration_part(domain, source, target, 'Swap', k)
                    migration = []
                    migration.append(migration_part)
 
                    for target_domain in targets:
                        #self.migrate(target_domain, target_node, source, K_VALUE)
                        migration_part = self.migration_part(target_domain, target_node, source, 'Swap', k)
                        migration.append(migration_part)
                        
                    migration_queue.append(migration)
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
                #self.migrate(domain, source, target, K_VALUE)   
                part = self.migration_part(domain, source, target, 'Underload', k) 
                migration = []
                migration.append(part)
                migration_queue.append(migration)                                
                raise StopIteration()
            
    
    def volume(self, node, k):
        # Calculates volume for node and return node
        volume = 1.0 / max(0.001, float(100.0 - node.percentile_load(PERCENTILE, k)) / 100.0)
        node.volume = volume
        node.volume_size = volume / 8.0 # 8 GByte
        
        return node    

            
    def normalized_volume(self, node, k):
        # Based on DRS, but use of volume as entitlement
        volume_domains = 0
        
        for domain in node['domains'].itervalues():
            volume_domains += domain['volume']

        print 'node: %s; normalized volume: %s' % (node['name'], volume_domains / 100)   
        # TODO: divide by node capacity
        
        return volume_domains / 100
            
                
    def imbalance(self, nodes, k):
        # Based on DRS     
        normalized_volumes = []
        
        for node in nodes.itervalues():
            volume = self.normalized_volume(node, k)
            
            if volume != 0.0:
                normalized_volumes.append(volume)

        return math.fabs(numpy.std(normalized_volumes))
    
    
    def migration_part(self, domain, source, target, description, k):
        return {
                'domain' : domain,
                'source' : source,
                'target' : target,
                'description' : description,
                'k' : k
                }
    
    def migration_scheduler(self):
        print 'START SCHEDULER; %s MIGRATIONS TO DO' % (len(migration_queue))

        target_nodes = []
        for migration in migration_queue:
            
            for part in migration:
                domain = part['domain']
                source = part['source']
                target = part['target']
                description = part['description']
                k = part['k']
                
                print '%s migration: %s from %s to %s' % (description, domain.name, source.name, target.name)
                self.migrate(domain, source, target, k)
                
                if target.name in target_nodes:
                    # If target was already a target in this cycle -> wait
                    print 'HERE SHOULD BE A BREAK'
                
                target_nodes.append(target.name)
                
            migration_queue.remove(migration)
        
        
  
        
        