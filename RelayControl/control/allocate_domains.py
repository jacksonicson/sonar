from ipmodels import ssapv
from service import times_client
from virtual import allocation as virt
from virtual import nodes
from workload import profiles
import domains
import numpy as np

def build_allocation(server_capacity=150, migrate=False):
    print 'Connecting with Times'
    connection = times_client.connect()
    
    # Loading services to combine the dmain_service_mapping with    
    services = profiles.selected
    service_count = len(domains.domain_profile_mapping)
    service_matrix = np.zeros((service_count, profiles.PROFILE_WIDTH), dtype=float)
    
    for s in xrange(service_count):
        mapping = domains.domain_profile_mapping[s]
        
        service = services[mapping.profile].name + profiles.POSTFIX_NORM
        print 'loading service: %s' % (service)
        
        ts = connection.load(service)
        ts_len = len(ts.elements)
    
        data = np.empty((ts_len), dtype=float)
        for i in xrange(ts_len):
            data[i] = ts.elements[i].value
            
        data = data[0:profiles.PROFILE_WIDTH]
        service_matrix[s] = data
        
    
    times_client.close()
    
    print 'Solving model...'
    server, assignment = ssapv.solve(len(nodes.HOSTS), server_capacity, service_matrix)
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
    build_allocation()


