from model import types
from virtual import nodes
import math
import numpy

class Imbalance():
    
    def __init__(self, controller, percentile, threshold_imbalance, min_improvement_imbalance, threshold_overload, node_capacity):
        self.controller = controller
        
        global PERCENTILE 
        PERCENTILE = percentile
        
        global THRESHOLD_IMBALANCE
        THRESHOLD_IMBALANCE = threshold_imbalance
        
        global MIN_IMPROVEMENT_IMBALANCE
        MIN_IMPROVEMENT_IMBALANCE = min_improvement_imbalance
        
        global THRESHOLD_OVERLOAD 
        THRESHOLD_OVERLOAD = threshold_overload
        
        global NODE_CAPACITY
        NODE_CAPACITY = node_capacity
    
    def migrate_imbalance(self, time_now, sleep_time, k):
        # based on DSR algorithm
        
        # create snapshot of nodes and domains
        system_nodes = self.controller.model.get_hosts(types.NODE)
        nodes = {}
        domains = {}
        migrations = {}
        for node in system_nodes:
            node_domains = {}
            
            for domain in node.domains.values():            
                new_domain = {}
                new_domain['name'] = domain.name
                new_domain['cpu'] = nodes.domain_to_server_cpu(node, domain, domain.percentile_load(PERCENTILE, k))
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
                source_node = self.controller.model.get_host(source['name'])
                
                if len(source['domains']) == 1:
                    # don't consider domains, which are alone on one node
                    continue
          
                for node in tmp_nodes.itervalues():
                    # consider every node as new parent for domain
                    
                    # calculate new cpu
                    target_node = self.controller.model.get_host(node['name'])
                    target_domain = self.controller.model.get_host(domain['name'])
                    node_cpu = node['cpu']
                    new_domain_cpu = nodes.domain_to_server_cpu(target_node, target_domain, target_domain.percentile_load(PERCENTILE, k))
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
            domain = self.controller.model.get_host(migration['domain'])
            source = self.controller.model.get_host(migration['source'])
            target = self.controller.model.get_host(migration['target'])
            
            self.controller.migration_scheduler.add_migration(domain, source, target, 'Imbalance') 
            self.controller.migration_triggered = True
            
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