from logs import sonarlog
from model import types
import json
import controller
import numpy
import math
import util

######################
## CONFIGURATION    ##
######################
START_WAIT = 0
INTERVAL = 20
THRESHOLD_OVERLOAD = 90
THRESHOLD_UNDERLOAD = 40
PERCENTILE = 80.0
THRESHOLD_IMBALANCE = 15
MIN_IMPROVEMENT_IMBALANCE = 2

K_VALUE = 20 # sliding windows size
M_VALUE = 17 # m values out of the window k must be above or below the threshold
######################

# Setup logging
logger = sonarlog.getLogger('controller')

# Migration Queue
migration_queue = []

class Sandpiper(controller.LoadBalancer):
    
    def __init__(self, pump, model):
        super(Sandpiper, self).__init__(pump, model, INTERVAL)
        
        
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
        
        
    def post_migrate_hook(self, success, domain, node_from, node_to, end_time):
        if success:
            # Release block
            time_now = self.pump.sim_time()
            node_from.blocked = time_now
            node_to.blocked = time_now
            
            # Reset CPU consumption: Necessary because the old CPU readings
            # may trigger another migrations as they do not represent the load
            # without the VM
            node_from.flush(50)
            node_to.flush(50)
            
            # Set finished status True
            for migration in migration_queue:
                domain2 = migration['domain']
                source2 = migration['source']
                target2 = migration['target']
                
                if domain.name == domain2.name and source2.name == node_from.name and target2.name == node_to.name:
                    migration['finished'] = True
                    self.migration_scheduler()
        else:
            
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
    
    
    def migration(self, domain, source, target, migration_type, k):
        return {
                'domain' : domain,
                'source' : source,
                'target' : target,
                'migration_type' : migration_type,
                'k' : k,
                'triggered' : False,
                'finished' : False
                }
    
    
    def volume(self, node, k):
        # Calculates volume for node and return node
        volume = 1.0 / max(0.001, float(100.0 - node.percentile_load(PERCENTILE, k)) / 100.0)
        node.volume = volume
        node.volume_size = volume / 8.0 # 8 GByte
        
        return node    

            
    def normalized_volume(self, node, k):
        # Based on DRS, but use of server load as entitlement

        h = self.model.get_host(node['name'])

        return h.percentile_load(PERCENTILE, k)
            
                
    def imbalance(self, nodes, k):
        # Based on DRS     
        normalized_volumes = []
        
        for node in nodes.itervalues():
            volume = self.normalized_volume(node, k)
            
            if len(node['domains']) != 0:
                normalized_volumes.append(volume)

        return math.fabs(numpy.std(normalized_volumes))
    
    
    def balance(self):
        
        sleep_time = 10
        time_now = self.pump.sim_time()
        
        ############################################
        ## IMBALANCE MIGRATION #####################
        ############################################
        
        self.migrate_imbalance(time_now, sleep_time, K_VALUE)
        
        if len(migration_queue) != 0:
            # if imbalance algorithm triggered migration, no further migrations will be executed
            return
        
        
        
        ############################################
        ## OVERLOAD/UNDERLOAD/SWAP MIGRATION #######
        ############################################
        
        # detect hotspots
        self.hotspot_detector()
            
        # calculate and sort nodes by their volume
        nodes = self.migration_manager()
        
        # trigger migration
        self.migration_trigger(nodes, sleep_time, time_now)
       
 
    def migrate_imbalance(self, time_now, sleep_time, k):
        # based on DSR algorithm from VMWare Paper
        
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
        print 'Imbalance: %s' % (imbalance)
        
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
                    
                    # calculate new load
                    target_node = self.model.get_host(node['name'])
                    target_domain = self.model.get_host(domain['name'])
                    node_cpu = target_node.percentile_load(PERCENTILE, k)
                    domain_cpu = util.domain_to_server_cpu(target_node, target_domain, target_domain.percentile_load(PERCENTILE, k))
                    target_threshold = node_cpu + domain_cpu
                    
                    if node['name'] == source['name'] or len(node['domains']) == 0 or target_threshold > THRESHOLD_OVERLOAD:
                        # don't migrate to same node nor empty node nor if overload threshold is exceeded
                        continue
                    
                    
                    # migrate domain to node and check new imbalance
                    node['domains'][domain['name']] = domain
                    new_imbalance = self.imbalance(tmp_nodes, k)
                    improvement = imbalance - new_imbalance
                    
                    if improvement > MIN_IMPROVEMENT_IMBALANCE and improvement > best_improvement:
                        best_migration = {'domain': domain['name'], 'source': source['name'], 'target': node['name']}
                        best_improvement = improvement
                        #print 'IMBALANCE TRIGGERED; imb bef: %s, imb aft: %s, imrov: %s' % (imbalance, new_imbalance, improvement)
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
                migration = self.migration(domain, source, target, 'Imbalance', k) 
                migration_queue.append(migration)    
        
        self.migration_scheduler()

        
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
                    node_domains.sort(lambda a, b: int((b.volume_size - a.volume_size) * 100000))
                    
                    # Try to migrate all domains by decreasing VSR value
                    for domain in node_domains:
                        self.migrate_overload(node, nodes, source, domain, time_now, sleep_time, K_VALUE, False)
                        self.swap(node, nodes, source, domain, time_now, sleep_time, K_VALUE)
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
                    node_domains.sort(lambda a, b: int((b.volume_size - a.volume_size) * 100000))
                    
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
                migration = self.migration(domain, source, target, 'Overload', k) 
                migration_queue.append(migration)    
                self.migration_scheduler()
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
                #self.migrate(domain, source, target, K_VALUE)   
                migration = self.migration(domain, source, target, 'Underload', k) 
                migration_queue.append(migration)    
                self.migration_scheduler()                            
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
                    migration = self.migration(domain, source, target_node, 'Swap', k)
                    migration_queue.append(migration)
 
                    for target_domain in targets:
                        migration = self.migration(target_domain, target_node, source, 'Swap', k)
                        migration_queue.append(migration)
                    
                    self.migration_scheduler()
                    raise StopIteration() 

        
    def migration_scheduler(self):
        print 'START SCHEDULER; %s MIGRATIONS TO DO' % (len(migration_queue))

        for migration in migration_queue:
            
            domain = migration['domain']
            source = migration['source']
            target = migration['target']
            migration_type = migration['migration_type']
            k = migration['k']
            triggered = migration['triggered']
            finished = migration['finished']
            
            if finished == True:
                migration_queue.remove(migration)
                continue
            
            skip = False
            
            for another_migration in migration_queue:
                target2 = another_migration['target']
                triggered2 = another_migration['triggered']
                finished2 = another_migration['finished']
                
                if migration != another_migration and target.name == target2.name and finished2 == False and triggered2 == True:
                    # There is another migration with same target node that isn't finished yet
                    # -> skip this migration until another migration is finished
                    skip = True
     
            if skip == True or triggered == True:
                continue
            
            print '%s migration: %s from %s to %s' % (migration_type, domain.name, source.name, target.name)
            import time
            time.sleep(2)
            migration['triggered'] = True
            self.migrate(domain, source, target, k) 
            
