from ipmodels import ssapv, dsap
from service import times_client
#from virtual import allocation as virt, nodes
from workload import profiles
import domains
import numpy as np

def build_allocation(nodecount, node_capacity=150, migrate=False):
    print 'Connecting with Times'
    connection = times_client.connect()
    
    # Loading services to combine the dmain_service_mapping with    
    services = profiles.selected
    service_count = len(domains.domain_profile_mapping)
    service_matrix = np.zeros((service_count, profiles.PROFILE_WIDTH), dtype=float)
    
    for s in xrange(service_count):
        mapping = domains.domain_profile_mapping[s]
        
        service = services[mapping.profileId].name + profiles.POSTFIX_USER + profiles.POSTFIX_TRACE
        print 'loading service: %s' % (service)
        
        ts = connection.load(service)
        ts_len = len(ts.elements)
    
        data = np.empty((ts_len), dtype=float)
        for i in xrange(ts_len):
            data[i] = ts.elements[i].value
            
        data = data[0:profiles.PROFILE_WIDTH]
        service_matrix[s] = data
        # print data
        
    
    times_client.close()
    
    print 'Solving model...'
    server, assignment = dsap.solve(nodecount, node_capacity, service_matrix)
    
    
    server, assignment = ssapv.solve(nodecount, node_capacity, service_matrix)
    if assignment != None:
        
        print 'Required servers: %i' % (server)
        print assignment
        
        print 'Assigning domains to servers'
        migrations = []
        for key in assignment.keys():
            mapping = domains.domain_profile_mapping[key]
            migration = (mapping.domain, assignment[key])
            migrations.append(migration)
        
        print migrations
        
        if migrate:
            print 'Migrating...'
            virt.migrateAllocation(migrations)
        
    else:
        print 'model infeasible'
    

if __name__ == '__main__':
    nodecount = 6 # len(nodes.HOSTS)
    build_allocation(nodecount, 300, False)


