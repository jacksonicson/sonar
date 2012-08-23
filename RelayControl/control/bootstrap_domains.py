from ipmodels import ssapv
from numpy import empty
from service import times_client
from virtual import allocation as virt
from workload import profiles
import matplotlib.pyplot as plt
import numpy as np


def normalize(data):
    mv = np.max(data)
    if mv > 0:
        data /= (mv)
        data *= 100
    return data


domain_service_mapping = [
                   ('glassfish0', 4),
                   ('glassfish1', 10),
                   ('glassfish2', 2),
                   ('glassfish3', 4),
                   ('glassfish4', 5),
                   ('glassfish5', 6),
                   ('mysql0', 4),
                   ('mysql1', 10),
                   ('mysql2', 2),
                   ('mysql3', 3),
                   ('mysql4', 4),
                   ('mysql5', 5),
                   ]

def main():
    print 'Connecting with Times'
    connection = times_client.connect()
    
    # Loading services to combine the dmain_service_mapping with    
    services = profiles.mix0
    service_count = len(domain_service_mapping)
    service_matrix = np.zeros((service_count, profiles.mix0_profile_width), dtype=float)
    
    for s in xrange(service_count):
        mapping = domain_service_mapping[s]
        
        service = services[mapping[1]][0] + '_profile'
        ts = connection.load(service)
        ts_len = len(ts.elements)
    
        data = np.empty((ts_len), float)
        for i in xrange(ts_len):
            data[i] = ts.elements[i].value
            
        data = normalize(data)
        service_matrix[s] = data
        
    
    times_client.close()
    
    
    print 'Solving model...'
    server, assignment = ssapv.solve(len(virt.HOSTS), 300, service_matrix)
    if assignment != None:
        
        print 'Required servers: %i' % (server)
        print assignment
        
        print 'Assigning domains to servers'
        migrations = []
        for key in assignment.keys():
            mapping = domain_service_mapping[key]
            migration = (mapping[0], assignment[key])
            migrations.append(migration)
            
        print migrations
        
        print 'Migrating...'
        virt.handleMigrations(migrations)
        
        
    else:
        print 'model infeasible'
    


if __name__ == '__main__':
    main()


