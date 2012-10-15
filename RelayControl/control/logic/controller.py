from model import types
from threading import Thread
import driver
import model
import numpy as np
import time

class LoadBalancer(Thread):
    '''
    Load balancer which design originated from Sandpiper
    '''
    
    def __init__(self, model):
        super(LoadBalancer, self).__init__()
        
        self.model = model
    
    
    def forecast(self, data):
        import statsmodels.api as sm
        import statsmodels as sm2

        model = sm2.tsa.ar_model.AR(data).fit()
        try:
            value = model.predict(len(data), len(data) + 1)
            return value[0]
        except:
            return data[-1]
        
        
    def migrate(self, domain, source, target):
        assert(target != source)
        now_time = time.time()
        target.blocked = now_time
        source.blocked = now_time
        
        target.domains[domain.name] = domain
        del source.domains[domain.name]
        
    
    def run(self):
        while True:
            # Sleeping till next balancing operation
            time.sleep(5)
            print 'Running load balancer...'
            
            ############################################
            ## HOTSPOT DETECTOR ########################
            ############################################
            
            for node in model.get_hosts(types.NODE):
                # Check past readings
                readings = node.get_readings()
                
                # m out of the k last measurements are used to detect overloads 
                k = 5 
                overload = 0
                underload = 0
                for reading in readings[-k:]:
                    if reading > 80: overload += 1
                    if reading < 40: underload += 1

                m = 3
                overload = (overload >= m)
                underload = (underload >= m)
                 
                if overload:
                    print 'Overload in %s - %s' % (node.name, readings[-k:])  
                 
                # Update overload                                
                node.overloaded = overload
                node.underloaded = underload
                
                
            ############################################
            ## MIGRATION MANAGER #######################
            ############################################
            # Calculate volumes of each node
            nodes = []
            domains = []
            for node in model.get_hosts():
                volume = 1.0 / max(0.001, float(100.0 - node.mean_load(k)) / 100.0)
                node.volume = volume
                node.volume_size = volume / 8.0 # 8 GByte
                
                if node.type == types.NODE:
                    nodes.append(node)
                elif node.type == types.DOMAIN: 
                    domains.append(node)
           
            # Sort nodes to their volume in DECREASING order
            # Multiplication with a big value to shift post comma digits to the front (integer)
            nodes.sort(lambda a, b: int((b.volume - a.volume) * 100000))
           
            
            ############################################
            ## MIGRATION TRIGGER #######################
            ############################################
            block_time = 30
            now_time = time.time()
            for node in nodes:
                node.dump()
                
                try:
                    # Overload situation
                    if node.overloaded:
                        # Source node to migrate from 
                        source = node
                        
                        # Sort domains by their VSR value in decreasing order 
                        node_domains = []
                        node_domains.extend(node.domains.values())
                        node_domains.sort(lambda a, b: int(b.volume_size - a.volume_size))
                        
                        # Try to migrate all domains by decreasing VSR value
                        for domain in node_domains:
                            
                            # Try all targets for the migration (reversed - starting at the BOTTOM)
                            for target in reversed(range(nodes.index(node) + 1, len(nodes))):
                                target = nodes[target]
                                 
                                test = True
                                test &= target.mean_load(k) + domain.mean_load(k) < 100
                                test &= (now_time - target.blocked) > block_time
                                test &= (now_time - source.blocked) > block_time
                                
                                if test: 
                                    print 'Overload migration: %s from %s to %s' % (domain.name, source.name, target.name)
                                    self.migrate(domain, source, target)
                                    raise StopIteration()
                except StopIteration: pass 
                
                try:
                    # Underload  situation
                    if node.underloaded:
                        # Source node to migrate from 
                        source = node
                        
                        # Sort domains by their VSR value in decreasing order 
                        node_domains = []
                        node_domains.extend(node.domains.values())
                        node_domains.sort(lambda a, b: int(b.volume_size - a.volume_size))
                        
                        # Try to migrate all domains by decreasing VSR value
                        for domain in node_domains:
                            
                            # Try all targets for the migration (reversed - starting at the underload domain walking TOP)
                            for target in reversed(range(0, nodes.index(node))):
                                target = nodes[target]
                                
                                test = True
                                test &= target.mean_load(k) + domain.mean_load(k) < 100
                                test &= (now_time - target.blocked) > block_time
                                test &= (now_time - source.blocked) > block_time
                                
                                if test: 
                                    print 'Underload migration: %s from %s to %s' % (domain.name, source.name, target.name)
                                    self.migrate(domain, source, target)                                    
                                    raise StopIteration()
                except StopIteration: pass 

                
class MetricHandler:
    '''
    Receives metric data from the simulation or from Sonar
    and feeds the data into the model. The data is later used
    by the load balancer to resolve over- and underloads.
    '''
    def receive(self, data):
        hostname = data.id.hostname
        
        host = model.get_host(hostname)
        if host == None:
            return
         
        host.put(data.reading)
        return


def build_from_current_allocation():
    from virtual import allocation
    allocation = allocation.determine_current_allocation()
    
    for host in allocation.iterkeys():
        node = model.Node(host)
        
        for domain in allocation[host]:
            node.add_domain(model.Domain(domain))
    

def build_initial_model():
    # Build model from current allocation
    build_from_current_allocation()
    
    # Dump model
    model.dump()
    
    # Initialize controller specific variables
    for host in model.get_hosts():
        host.blocked = 0


if __name__ == '__main__':
    # Build internal infrastructure representation
    build_initial_model()

    # Create notification handler
    handler = MetricHandler()
    
    # Start the driver thread which simulates Sonar
    driver = driver.Driver(model, handler)
    driver.start()
    
    # Connect with sonar to receive metric readings
    # connector.connect_sonar(model, handler)
    
    # Start load balancer thread which detects hotspots and triggers migrations
    balancer = LoadBalancer(model)
    balancer.start() 
        
