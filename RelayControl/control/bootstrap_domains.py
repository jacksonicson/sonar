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


def main():
    print 'Connecting with Times'
    connection = times_client.connect()
    
    print 'Querying for TS data...'
    services = profiles.mix0
    service_count = len(services)
    
    service_matrix = np.zeros((service_count, 111), dtype=float)
    
    for s in xrange(service_count):
        service = services[s][0] + '_profile'
        ts = connection.load(service)
        
        ts_len = len(ts.elements)
        print '%s - %i' % (service, ts_len)
    
        data = np.empty((ts_len), float)
        for i in xrange(ts_len):
            data[i] = ts.elements[i].value
            
        data = normalize(data)
        try:
            service_matrix[s] = data
        except:
            print 'WARN: PROFILE CONSITENCY PROBLEM OCCURED'
        
    
    times_client.close()
    
    print 'Solving model...'
    server, assignment = ssapv.solve(len(virt.HOSTS), 400, service_matrix)
    if assignment != None:
        print server
        print assignment
        
        print 'Assigning domains to servers'
        domain_workload_mapping = {
                   'glassfish0' : 0, 
                   }
        
    else:
        print 'model infeasible'
    


if __name__ == '__main__':
    main()
