from control import domains
from ipmodels import ssapv, dsap
from logs import sonarlog
from service import times_client
from virtual import allocation as virt, nodes
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
    
    def execute(self):
        # Dump profiles
        profiles.dump(logger)
        
        # Dump nodes configuration
        nodes.dump(logger)
        
        # Dump mapping
        domains.dump(logger)
        
   
class RRPlacement(Placement):
    def execute(self):
        print 'Distributing domains over all servers ...'
    
        # Dump profiles
        profiles.dump(logger)
        
        # Dump nodes configuration
        nodes.dump(logger)
        
        # Dump mapping
        domains.dump(logger)
        
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
        
        return migrations
    
    
class SSAPvPlacement(Placement):
    
    def execute(self):
        # Execute super code
        super(SSAPvPlacement, self).execute()
        
        # Connect with Times
        print 'Connecting with Times'
        connection = times_client.connect()
        
        # Loading services to combine the dmain_service_mapping with    
        services = profiles.selected
        service_count = len(domains.domain_profile_mapping)
        service_matrix = np.zeros((service_count, profiles.PROFILE_WIDTH), dtype=float)
        
        service_log = ''
        for service_index in xrange(service_count):
            mapping = domains.domain_profile_mapping[service_index]
            
            # Important: Load the trace of the workload profile
            service = services[mapping.profileId].name + profiles.POSTFIX_TRACE
            print 'loading service: %s' % (service)
            service_log += service + '; '
            
            ts = connection.load(service)
            ts_len = len(ts.elements)
        
            # put TS into service matrix
            data = np.empty((ts_len), dtype=float)
            for i in xrange(ts_len):
                data[i] = ts.elements[i].value
                
            data = data[0:profiles.PROFILE_WIDTH]
    
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
        # server, assignment = dsap.solve(nodecount, node_capacity_cpu, node_capacity_mem, service_matrix, domain_demand_mem)
        server, assignment = ssapv.solve(self.nodecount, self.node_capacity_cpu, self.node_capacity_mem, service_matrix, self.domain_demand_mem)
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
            return migrations
    
        else:
            print 'model infeasible'
            return None
        
