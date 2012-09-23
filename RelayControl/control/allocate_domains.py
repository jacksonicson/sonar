from ipmodels import ssapv, dsap
from service import times_client
from virtual import nodes
from workload import profiles
import domains
import numpy as np
from virtual import allocation as virt
from logs import sonarlog

# Setup logging
logger = sonarlog.getLogger('allocate_domains', 'Andreas-PC')

def build_allocation(nodecount, node_capacity_cpu, node_capacity_mem, domain_demand_mem, migrate=False):
    # Dump profiles
    profiles.dump(logger)
    
    # Dump nodes configuration
    nodes.dump(logger)
    
    # Dump mapping
    domains.dump(logger)
    
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
    server, assignment = ssapv.solve(nodecount, node_capacity_cpu, node_capacity_mem, service_matrix, domain_demand_mem)
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

        if migrate:
            print 'Migrating...'
            virt.migrateAllocation(migrations)
        
    else:
        print 'model infeasible'
    
    
def build_null_allocation(nodecount, migrate=False):
    print 'Distributing domains over all servers ...'
    
    # Dump profiles
    profiles.dump(logger)
    
    # Dump nodes configuration
    nodes.dump(logger)
    
    # Dump mapping
    domains.dump(logger)
    
    # Logging
    logger.info('Placement strategy: Round Robin')
    logger.info('Required servers: %i' % nodecount)
    
    assignment, migrations = virt.get_null_allocation(nodecount)
    
    print 'Assignment: %s' % assignment
    logger.info('Assignment: %s' % assignment)
    print 'Migrations: %s' % migrations
    logger.info('Migrations: %s' % migrations)
    
    if migrate:
        print 'Migrating...'
        virt.migrateAllocation(migrations) 
    

if __name__ == '__main__':
    nodecount = len(nodes.HOSTS)
    # build_allocation(nodecount, nodes.NODE_CPU, nodes.NODE_MEM, nodes.DOMAIN_MEM, True)
    build_null_allocation(nodecount, migrate=False)


