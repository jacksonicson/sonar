from control.logic.model import types
from control.logic import util
import math
import numpy
import configuration_advanced

class Imbalance():
    
    def __init__(self, model, migration_scheduler):
        self.model = model
        self.migration_scheduler = migration_scheduler
        
        self.PERCENTILE = configuration_advanced.PERCENTILE
        self.THRESHOLD_IMBALANCE = configuration_advanced.THRESHOLD_IMBALANCE
        self.MIN_IMPROVEMENT_IMBALANCE = configuration_advanced.MIN_IMPROVEMENT_IMBALANCE
        self.THRESHOLD_OVERLOAD = configuration_advanced.THRESHOLD_OVERLOAD
        self.NODE_CAPACITY = configuration_advanced.NODE_CAPACITY
        self.K_VALUE = configuration_advanced.K_VALUE
    
    def migrate_imbalance(self, time_now, sleep_time):
        # based on DSR algorithm
        
        # create snapshot of nodes and domains
        system_nodes = self.model.get_hosts(types.NODE)
        nodes = {}
        domains = {}
        migrations = {}
        for node in system_nodes:
            node_domains = {}
            
            for domain in node.domains.values():            
                new_domain = Host()
                new_domain.name = domain.name
                new_domain.cpu = util.domain_to_server_cpu(node, domain, domain.percentile_load(self.PERCENTILE, self.K_VALUE))
                new_domain.source = node.name
                node_domains[domain.name] = new_domain
                domains[domain.name] = new_domain
                
            new_node = Host()
            new_node.name = node.name
            new_node.cpu = node.percentile_load(self.PERCENTILE, self.K_VALUE)
            new_node.domains = node_domains
            new_node.normalized_cpu = self.normalized_cpu(new_node)
            nodes[node.name] = new_node
        
        # run load balancing    
        imbalance = self.imbalance(nodes)
        print 'IMBALANCE %s' % (imbalance)
        num_migrations = 0
        max_migrations = 10
        
        while (imbalance > self.THRESHOLD_IMBALANCE) and (num_migrations < max_migrations):
            best_migration = None
            best_improvement = 0
            
            for domain in domains.itervalues():
                # for every domain
                tmp_nodes = nodes
                
                # save parent node extra
                source = tmp_nodes[domain.source]
                source_node = self.model.get_host(source.name)
                
                if len(source.domains) == 1:
                    # don't consider domains, which are alone on one node
                    continue
          
                for node in tmp_nodes.itervalues():
                    # consider every node as new parent for domain
                    
                    # calculate new cpu
                    target_node = self.model.get_host(node.name)
                    target_domain = self.model.get_host(domain.name)
                    new_domain_cpu = util.domain_to_server_cpu(target_node, target_domain, target_domain.percentile_load(self.PERCENTILE, self.K_VALUE))
                    old_domain_cpu = domain.cpu
                    domain.cpu = new_domain_cpu
                    target_threshold = node.cpu + new_domain_cpu
                    
                    # don't migrate domain to same node nor empty node nor if overload threshold is exceeded
                    test = False
                    test |= target_node.name == source_node.name
                    test |= len(target_node.domains) == 0
                    test |= len(target_node.domains) >= 6
                    test |= target_threshold > self.THRESHOLD_OVERLOAD
                    test |= (time_now - target_node.blocked) <= sleep_time
                    test |= (time_now - source_node.blocked) <= sleep_time
                    
                    if test:
                        continue
                    
                    # migrate domain to node (in snapshot) and check new imbalance
                    node.domains[domain.name] = domain
                    del source.domains[domain.name]
                    old_normalized_cpu_node = node.normalized_cpu
                    old_normalized_cpu_source = source.normalized_cpu
                    node.normalized_cpu = self.normalized_cpu(node)
                    source.normalized_cpu = self.normalized_cpu(source)
                    new_imbalance = self.imbalance(tmp_nodes)
                    improvement = imbalance - new_imbalance
                    
                    if improvement > self.MIN_IMPROVEMENT_IMBALANCE and improvement > best_improvement:
                        best_migration = Migration()
                        best_migration.domain = target_domain
                        best_migration.source = source_node
                        best_migration.target = target_node
                        
                        best_source = source
                        best_target = node
                        best_domain = domain
                        best_improvement = improvement                    
                    
                    # go back to previous state
                    domain.cpu = old_domain_cpu
                    source.domains[domain.name] = domain
                    source.normalized_cpu = old_normalized_cpu_source
                    del node.domains[domain.name]
                    node.normalized_cpu = old_normalized_cpu_node
                                
            if best_migration is None:
                break
            
            # update imbalance and new nodes with best_migration
            imbalance -= best_improvement 
            migrations[num_migrations] = best_migration
            best_domain.source = best_target.name
            best_target.domains[best_domain.name] = best_domain
            best_target.normalized_cpu = self.normalized_cpu(best_target)
            del best_source.domains[best_domain.name]
            best_source.normalized_cpu = self.normalized_cpu(best_source)
            num_migrations += 1
      
        # migrate domains that improve imbalance
        for migration in migrations.itervalues():            
            self.migration_scheduler.add_migration(migration.domain, migration.source, migration.target, 'Imbalance') 
            
        if len(migrations) != 0:
            return True
            
    def normalized_cpu(self, node):
        # Calculate normalized cpu of a node        
        load = 0
        for domain in node.domains.itervalues():
            load += domain.cpu
        
        return load / self.NODE_CAPACITY
            
    def imbalance(self, nodes):
        # Based on DRS     
        normalized_cpus = []
        for node in nodes.itervalues():
            if len(node.domains) != 0:
                normalized_cpus.append(node.normalized_cpu)

        return math.fabs(numpy.std(normalized_cpus))   
    
class Host(object):
    pass

class Migration(object):
    pass