from control.logic import placement
from virtual import nodes
from service import times_client
from workload import profiles, util as wutil
from control import domains
import matplotlib.pyplot as plt

def main():
    # Solve allocation problem
    nodecount = len(nodes.HOSTS)
    model = placement.SSAPvPlacement(nodecount, nodes.NODE_CPU, nodes.NODE_MEM, nodes.DOMAIN_MEM)
    model.execute()
    
    assignment = model.assignment
    if assignment != None:
        
        node_assignment = {}
        for domain in assignment.keys():
            node = assignment[domain]
            if not node_assignment.has_key(node):
                node_assignment[node] = []
            node_assignment[node].append(domain)
            
        print node_assignment 
                
        # Load time series used by the drivers
        # Connect with Times
        print 'Connecting with Times'
        tsdata = []
        connection = times_client.connect()
        
        # Loading services to combine the dmain_service_mapping with
        service_count = len(domains.domain_profile_mapping)
        import sys
        ts_length = sys.maxint
        for i_service in xrange(service_count):
            name = profiles.get_current_cpu_profile(i_service)
            tsd = connection.load(name)
            tsd = wutil.to_array(tsd)[1]
            tsdata.append(tsd)
            ts_length = min(ts_length, len(tsd)) 
            
        times_client.close()
        
        # Run simulation and report overload situations
        acc_load = [[] for _ in xrange(len(nodes.NODES))]
        for t in xrange(ts_length):
            print '-- t -- %i' % t
            for node in node_assignment.keys():
                sum_load = 0
                for domain in node_assignment[node]: 
                    sum_load += tsdata[domain][t]
                    
                print node
                acc_load[node].append(sum_load)

        # Plot accumulated loads
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.axis([0.0, ts_length, 0, 500])
        for load in acc_load:
            ax.plot(range(0, len(load)), load)
    
        plt.show()
             
    else:
        print 'Could not check overload - no feasible assignment found'
        
    

if __name__ == '__main__':
    main() 