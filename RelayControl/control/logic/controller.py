import model
from model import types
from threading import Thread
import time
import driver

class LoadBalancer(Thread):
    '''
    Load balancer which designed originated from Sandpiper
    '''
    
    def __init__(self, model):
        super(LoadBalancer, self).__init__()
        
        self.model = model
    
    def forecast(self, data):
        import statsmodels.api as sm
        import statsmodels as sm2

        model = sm2.tsa.ar_model.AR(data).fit()
        try:
            value = model.predict(len(data),len(data)+1)
            return value[0]
        except:
            return data[-1]
        
    
    def run(self):
        while True:
            # Sleeping till next balancing operation
            time.sleep(5)
            print 'Running load balancer...'
            
            ## HOTSPOT DETECTOR ########################
            for node in model.get_hosts():
                # Check past readings
                readings = node.get_readings()
                overload = 0
                underload = 0
                
                size = len(readings)
                
                # m out of the k last measurements are used to detect overloads 
                k = 5 
                m = 3
                
                for i in xrange(size - k, size):
                    if readings[i] > 80: overload += 1
                    if readings[i] < 20: underload += 1

                overload = overload >= m
                underload = underload >= m
                 
                # Check workload prediction
                forecast = self.forecast(readings)
                overload &= forecast > 75
                underload &= forecast < 20

                # Update overload                                
                node.overloaded = overload
                node.underloaded = underload
                
            ## MIGRATION MANAGER #######################
            # Calculate volumes of each node
            nodes = []
            domains = []
            for node in model.get_hosts():
                volume = 1.0 / max(0.001, (100.0 - node.mean_load()))
                node.volume = volume
                node.volume_size = volume / 8.0 # 8 GByte
                
                if node.type == types.NODE:
                    nodes.append(node)
                elif node.type == types.DOMAIN: 
                    domains.append(node)
                
            # Sort nodes to their volume in reverse order
            nodes.sort(lambda a, b: int(a.volume - b.volume))
            
            ## MIGRATION TRIGGER #######################
            for node in nodes:
                node.dump()
                
                # Underload situation
                if node.underloaded: 
                    node_domains = []
                    node_domains.extend(node.domains.values())
                    node_domains.sort(lambda a, b: int(a.volume_size - b.volume_size))
                    
                    try:
                        for domain in node_domains:
                            left = nodes.index(node)
                            for right in reversed(xrange(0, left)):
                                target = nodes[right]
                                
                                if len(target.domains) == 0: continue
                                
                                source = node
                                if nodes[right].mean_load() + domain.mean_load() < 100 and (time.time() - target.blocked) > 10 and (time.time() - source.blocked) > 10:
                                    print 'Underload migration: %s from %s to %s' % (domain.name, source.name, target.name)
                                    
                                    target.blocked = time.time()
                                    source.blocked = target.blocked 
                                    
                                    target.domains[domain.name] = domain
                                    del source.domains[domain.name]
                                    
                                    raise StopIteration()
                    except StopIteration:
                        pass 

                # Overload situation                
                if node.overloaded:
                    node_domains = []
                    node_domains.extend(node.domains.values())
                    node_domains.sort(lambda a, b: int(a.volume_size - b.volume_size))
                    
                    try:
                        for domain in node_domains:
                            left = nodes.index(node) + 1 
                            for right in xrange(left, len(nodes)):
                                target = nodes[right]
                                source = node
                                if nodes[right].mean_load() + domain.mean_load() < 100 and (time.time() - target.blocked) > 10 and (time.time() - source.blocked) > 10:
                                    print 'Overload migration: %s from %s to %s' % (domain.name, source.name, target.name)
                                    
                                    target.blocked = time.time()
                                    source.blocked = target.blocked
                                    
                                    target.domains[domain.name] = domain
                                    del source.domains[domain.name]
                                    
                                    raise StopIteration()
                    except StopIteration:
                        pass 
                 

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


def build_initial_model():
    # TODO: Read this somehow from Sonar or recreate initial allocation
    # if it was created by a deterministic algorithm
    node = model.Node('srv0')
    node.add_domain(model.Domain('target0'))
    node.add_domain(model.Domain('target1'))
    
    node = model.Node('srv1')
    node.add_domain(model.Domain('target2'))
    node.add_domain(model.Domain('target3'))
    
    node = model.Node('srv2')
    node = model.Node('srv3')
    node = model.Node('srv4')
    
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
        
