from control import domains
from ipmodels import ssapv
from ipmodels import dsap
from logs import sonarlog
from service import times_client
from virtual import nodes
from workload import profiles
import numpy as np
from control.domains import domain_profile_mapping as mapping

# Setup logging
logger = sonarlog.getLogger('allocate_domains')

class Placement(object):
    def __init__(self, nodecount, node_capacity_cpu, node_capacity_mem, domain_demand_mem):
        self.nodecount = nodecount
        self.node_capacity_cpu = node_capacity_cpu
        self.node_capacity_mem = node_capacity_mem
        self.domain_demand_mem = domain_demand_mem
    
    def _count_active_servers(self, assignment):
        buckets = [True for _ in xrange(len(nodes.HOSTS))]
        active_servers = 0
        active_server_list = []
        for service in assignment.keys():
            inode = assignment[service]
            if buckets[inode]:
                buckets[inode] = False
                active_servers += 1
                active_server_list.append(nodes.get_node_name(inode))
            
        return active_servers, active_server_list
            
    
    def execute(self):
        # Dump profiles
        profiles.dump(logger)
        
        # Dump nodes configuration
        nodes.dump(logger)
        
        # Dump mapping
        domains.dump(logger)
   
   
class RRPlacement(Placement):
    def execute(self):
        # Execute super code
        super(RRPlacement, self).execute()
        
        print 'Distributing domains over all servers ...'
            
        # Logging
        logger.info('Placement strategy: Round Robin')
        logger.info('Required servers: %i' % self.nodecount)
        
        
        migrations = []
        assignment = {}
        
        node_index = 0
        service_index = 0
        for maps in mapping:
            migrations.append((maps.domain, node_index))
            node_index = (node_index + 1) % self.nodecount
            
            assignment[service_index] = node_index
            service_index += 1
        
        print 'Assignment: %s' % assignment
        logger.info('Assignment: %s' % assignment)
        print 'Migrations: %s' % migrations
        logger.info('Migrations: %s' % migrations)
        
        return migrations, self._count_active_servers(assignment)
 
 
class FirstFitPlacement(Placement):
    def execute(self):
        # Execute super code
        super(FirstFitPlacement, self).execute()
        
        print 'Using First Fit for domain placmement ...'
            
        # Logging
        logger.info('Placement strategy: First Fit')
        logger.info('Required servers: %i' % len(nodes.HOSTS))
        
        # Connect with Times
        print 'Connecting with Times'
        connection = times_client.connect()
        
        # Loading services to combine the dmain_service_mapping with    
        service_count = len(domains.domain_profile_mapping)
        
        # For each node there is one bucket
        buckets = []
        migrations = []
        assignment = {}
        for _ in xrange(len(nodes.HOSTS)):
            buckets.append([0, nodes.NODE_CPU, []])
        
        # Service which gets mapped
        for service_index in xrange(service_count):
            # Maps the service to a service profile
            mapping = domains.domain_profile_mapping[service_index]
            
            # Important: Load the trace of the workload profile
            service = profiles.get_traced_cpu_profile(service_index)
            
            print 'loading service: %s' % (service)
            ts = connection.load(service)
            from workload import util
            _, demand = util.to_array(ts)
        
            # Determine max demand value of this service
            max_value = np.percentile(demand, 95) # np.max(demand)
            
            bin_found = False
            try:
                for node_index in xrange(len(buckets)):
                    bucket = buckets[node_index]
                    if (bucket[0] + max_value) < bucket[1]:
                        bin_found = True
                        
                        bucket[0] = bucket[0] + max_value
                        bucket[2].append(service)
                        
                        migrations.append((mapping.domain, node_index))
                        assignment[service_index] = node_index
                        
                        raise StopIteration()
            except StopIteration:
                if bin_found == False:
                    print 'WARN: Could not assign domain to a node!'
                  
                  
        # Close Times connection
        times_client.close()
        
              
        for bucket in buckets:
            print 'bucket length: %i' % len(bucket[2])
                  
        print 'Assignment: %s' % assignment
        logger.info('Assignment: %s' % assignment)
        print 'Migrations: %s' % migrations
        logger.info('Migrations: %s' % migrations)
           
        return migrations, self._count_active_servers(assignment)
         
            
    
class SSAPvPlacement(Placement):
    
    def execute(self):
        # Execute super code
        super(SSAPvPlacement, self).execute()
        
        # Connect with Times
        print 'Connecting with Times'
        connection = times_client.connect()
        
        # Loading services to combine the dmain_service_mapping with    
        service_count = len(domains.domain_profile_mapping)
        service_matrix = np.zeros((service_count, profiles.PROFILE_INTERVAL_COUNT), dtype=float)
        
        service_log = ''
        for service_index in xrange(service_count):
            mapping = domains.domain_profile_mapping[service_index]
            
            # Important: Load the trace of the workload profile
            service = profiles.get_traced_cpu_profile(mapping.profileId)
            
            print 'loading service: %s' % (service)
            service_log += service + '; '
            
            ts = connection.load(service)
            ts_len = len(ts.elements)
        
            # put TS into service matrix
            data = np.empty((ts_len), dtype=float)
            for i in xrange(ts_len):
                data[i] = ts.elements[i].value
                
            data = data[0:profiles.PROFILE_INTERVAL_COUNT]
    
            service_matrix[service_index] = data
            # print data
    
        # Log services
        logger.info('Selected profile: %s' % profiles.selected_name)
        logger.info('Loading services: %s' % service_log)
    
        # Dumpservice_matrix
        print 'Logging service matrix...'
        np.set_printoptions(linewidth=200, threshold=99999999)
        logger.info('Service matrix: %s' % service_matrix)
    
        # Close Times connection
        times_client.close()
        
        print 'Solving model...'
        logger.info('Placement strategy: SSAPv')
        server, assignment = ssapv.solve(self.nodecount, self.node_capacity_cpu, self.node_capacity_mem, service_matrix, self.domain_demand_mem)
        
        # Set assignment for getter functions 
        self.assignment = assignment
        
        if assignment != None:
            print 'Required servers: %i' % (server)
            logger.info('Required servers: %i' % server)
            print assignment
            logger.info('Assignment: %s' % assignment)
            
            print 'Assigning domains to servers'
            migrations = []
            for key in assignment.keys():
                mapping = domains.domain_profile_mapping[key]
                migration = (mapping.domain, assignment[key])
                migrations.append(migration)
            
            
            print 'Migrations: %s' % migrations
            logger.info('Migrations: %s' % migrations)
            return migrations, self._count_active_servers(assignment)
    
        else:
            print 'model infeasible'
            return None, None
        
        
  
class DSAPPlacement(Placement):
    
    def execute(self):
        # Execute super code
        super(DSAPPlacement, self).execute()
        
        # Connect with Times
        print 'Connecting with Times'
        connection = times_client.connect()
        
        # Loading services to combine the dmain_service_mapping with    
        service_count = len(domains.domain_profile_mapping)
        service_matrix = np.zeros((service_count, profiles.PROFILE_INTERVAL_COUNT), dtype=float)
        
        service_log = ''
        for service_index in xrange(service_count):
            mapping = domains.domain_profile_mapping[service_index]
            
            # Important: Load the trace of the workload profile
            service = profiles.get_traced_cpu_profile(mapping.profileId)
            
            print 'loading service: %s' % (service)
            service_log += service + '; '
            
            ts = connection.load(service)
            ts_len = len(ts.elements)
        
            # put TS into service matrix
            data = np.empty((ts_len), dtype=float)
            for i in xrange(ts_len):
                data[i] = ts.elements[i].value
                
            data = data[0:profiles.PROFILE_INTERVAL_COUNT]
    
            service_matrix[service_index] = data
            # print data
    
        # Log services
        logger.info('Selected profile: %s' % profiles.selected_name)
        logger.info('Loading services: %s' % service_log)
    
        # Dumpservice_matrix
        print 'Logging service matrix...'
        np.set_printoptions(linewidth=200, threshold=99999999)
        logger.info('Service matrix: %s' % service_matrix)
    
        # Close Times connection
        times_client.close()
        
        # Apply downsampling
        
        
        
        print 'Solving model...'
        logger.info('Placement strategy: DSAP')
        server, assignment_list = dsap.solve(self.nodecount, self.node_capacity_cpu, self.node_capacity_mem, service_matrix, self.domain_demand_mem)
                
        # return initial placement - A(0) only
        assignment = assignment_list[0]
        
#        print "DEBUG: assignment_list ", assignment_list
#        print "DEBUG: assignment_list[0] ", assignment_list[0]
        
        # Set assignment for getter functions 
        self.assignment = assignment
        
        if assignment != None:
            print 'Required servers: %i' % (server)
            logger.info('Required servers: %i' % server)
            print assignment
            logger.info('Assignment: %s' % assignment)
            
            print 'Assigning domains to servers'
            migrations = []
            for key in assignment.keys():
                mapping = domains.domain_profile_mapping[key]
                migration = (mapping.domain, assignment[key])
                migrations.append(migration)
            
            
            print 'Migrations: %s' % migrations
            logger.info('Migrations: %s' % migrations)
            return migrations, self._count_active_servers(assignment)
    
        else:
            print 'model infeasible'
            return None, None