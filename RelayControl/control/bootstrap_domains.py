from virtual import allocation as virt
from ipmodels import ssapv
import times_client
from numpy import empty
import numpy as np
import matplotlib.pyplot as plt

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
    items = connection.find('O2.*_profile')
    
    ts = connection.load(items[0])
    
    data = empty((len(items), 300), dtype=float)
    for t in xrange(len(items)):
        item = items[t]
        ts = connection.load(item)
        
        for i in xrange(len(ts.elements)):
            value = ts.elements[i].value
            data[t,i] = value
            
        data[t] = normalize(data[t])
            
        fig = plt.figure(figsize=(12, 9))
        ax = fig.add_subplot(211)
        ax.plot(range(len(data[t])), data[t])
        # plt.show()
    
    times_client.close()
    
    print 'Solving model...'
    server, assignment = ssapv.solve(len(virt.HOSTS), 100, data)
    
    if assignment != None:
        print 'Transferring assignment to infrastructure'
        # Create VM target plan
        domains = []
        domains.extend('glassfish%i' % (i) for i in xrange(6))
        domains.extend('mysql%i' % (j) for j in xrange(6))
        
        allocation = []
        for key in assignment.keys():
            allocation.append((domains[key], assignment[key]))
        
        print allocation
        # allocation.handleMigrations(allocation)
        
    else:
        print 'Model could not be solved!'
    


if __name__ == '__main__':
    main()