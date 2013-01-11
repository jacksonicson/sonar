from control import domains
from control.domains import domain_profile_mapping as mapping
from ipmodels import ssapv
from ipmodels import dsap
from logs import sonarlog
from service import times_client
from virtual import nodes
from workload import profiles
from workload.timeutil import * #@UnusedWildImport
import numpy as np

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
            
    '''
    Returns a tuple of migrations and number of active servers. Migrations is a dictionary 
    with domain indices as keys and node indices as values. 
    [domain index] -> server index  
    '''
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
        buckets_mem = []
        
        migrations = []
        assignment = {}
        for _ in xrange(len(nodes.HOSTS)):
            buckets.append([0, nodes.NODE_CPU, []])
            buckets_mem.append([0, nodes.NODE_MEM, []])
        
        # Service which gets mapped
        for service_index in xrange(service_count):
            # Maps the service to a service profile
            mapping = domains.domain_profile_mapping[service_index]
            
            # Important: Load the trace of the workload profile
            service = profiles.get_cpu_profile_for_initial_placement(service_index)
            
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
                    bucket_mem = buckets_mem[node_index]
                    if (bucket[0] + max_value) < bucket[1] and (bucket_mem[0] + nodes.DOMAIN_MEM) < bucket_mem[1]:
                        bin_found = True
                        
                        bucket[2].append(service)
                        
                        bucket[0] = bucket[0] + max_value
                        bucket_mem[0] = bucket_mem[0] + nodes.DOMAIN_MEM
                        
                        migrations.append((mapping.domain, node_index))
                        assignment[service_index] = node_index
                        
                        raise StopIteration()
                print 'Error no target!'
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
    
    def execute(self, aggregation=False, bucketCount=24):
        # Execute super code
        super(SSAPvPlacement, self).execute()
        
        # Connect with Times
        print 'Connecting with Times'
        connection = times_client.connect()
        
        # Loading services to combine the dmain_service_mapping with    
        service_count = len(domains.domain_profile_mapping)
        
        if aggregation:
            llen = bucketCount
        else: 
            llen = profiles.PROFILE_INTERVAL_COUNT
        service_matrix = np.zeros((service_count, llen), dtype=float)
        
        service_log = ''
        for service_index in xrange(service_count):
            mapping = domains.domain_profile_mapping[service_index]
            service = profiles.get_cpu_profile_for_initial_placement(mapping.profileId)
                
            print 'loading service: %s' % (service)
            service_log += service + '; '
            
            ts = connection.load(service)
            ts_len = len(ts.elements)
        
            # put TS into service matrix
            data = np.empty((ts_len), dtype=float)
            for i in xrange(ts_len):
                data[i] = ts.elements[i].value
                
            
            data = data[0:profiles.PROFILE_INTERVAL_COUNT]
    
            # Downsample TS
            if aggregation:
                elements = ts_len / bucketCount
                bucket_data = []
                for i in xrange(bucketCount):
                    start = i * elements
                    end = min(ts_len, (i + 1) * elements)
                    tmp = data[start : end]
                    bucket_data.append(np.max(tmp))
                service_matrix[service_index] = bucket_data
            else:
                service_matrix[service_index] = data
    
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

    def execute(self, num_buckets):
        from workload import util
                
        # Execute super code
        super(DSAPPlacement, self).execute()
        
        # Connect with Times
        print 'Connecting with Times'
        connection = times_client.connect()
        
        # Loading services to combine the dmain_service_mapping with    
        domain_count = len(domains.domain_profile_mapping)
        domain_matrix = np.zeros((domain_count, num_buckets), dtype=float)
        
        domain_log = ''
        for domain_index in xrange(domain_count):
            mapping = domains.domain_profile_mapping[domain_index]
            
            # Important: Load the trace of the workload profile
            domain = profiles.get_cpu_profile_for_initial_placement(mapping.profileId)
            
            print 'loading domain: %s' % (domain)
            domain_log += domain + '; '
            
            ts = connection.load(domain)
            ts_len = len(ts.elements)
        
            # put TS into domain matrix
            _time, data = util.to_array(ts)
            
            data = data[0:profiles.PROFILE_INTERVAL_COUNT]
            
            # Downsampling TS (domain_matrix)
            self.experiment_length = ts_len * ts.frequency  # length of the experiment measured in seconds
            bucket_width = self.experiment_length / num_buckets # in sec
            
            #elements = bucket_width / ts.frequency
            elements = ts_len / num_buckets
            buckets = []
            for i in xrange(num_buckets):
                start = i * elements
                end = min(ts_len, (i+1) * elements) 
                tmp = data[start : end]
                buckets.append(np.mean(tmp))
    
            domain_matrix[domain_index] = buckets
            # print data
    
        # Log services
        logger.info('Selected profile: %s' % profiles.selected_name)
        logger.info('Loading services: %s' % domain_log)
    
        # Dumpservice_matrix
        print 'Logging domain matrix...'
        np.set_printoptions(linewidth=200, threshold=99999999)
        logger.info('Service matrix: %s' % domain_matrix)
    
        # Close Times connection
        times_client.close()
        
        print "Downsampling-Ratio:",ts_len,"elements TO",num_buckets,"buckets (freq=",ts.frequency,", placement.experiment_length=",self.experiment_length,", profiles.experiment_duration",profiles.EXPERIMENT_DURATION,")"
        
        print 'Solving model...'
        logger.info('Placement strategy: DSAP')
        server_list, assignment_list = dsap.solve(self.nodecount, self.node_capacity_cpu, self.node_capacity_mem, domain_matrix, self.domain_demand_mem)
                
        # return values for initial placement only > A(0) <   (#servers + assignment(t=0))
        self.assignment_list = assignment_list
        initial_placement = assignment_list[0]
        
        self.server_list = server_list
        initial_server_count = server_list[0]
        
        # Set initial_placement for getter functions 
        if initial_placement != None:
            print 'Required servers: %i' % (initial_server_count)
            logger.info('Required servers: %i' % initial_server_count)
            print initial_placement
            logger.info('Assignment: %s' % initial_placement)
            
            print 'Assigning domains to servers'
            migrations = []
            for key in initial_placement.keys():
                mapping = domains.domain_profile_mapping[key]
                migration = (mapping.domain, initial_placement[key])
                migrations.append(migration)
            
            print 'Migrations: %s' % migrations
            logger.info('Migrations: %s' % migrations)
            return migrations, self._count_active_servers(initial_placement)
    
        else:
            print 'model infeasible'
            return None, None
