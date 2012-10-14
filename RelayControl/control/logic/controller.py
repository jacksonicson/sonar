from control.logic import model
from model import Node, Domain, types, get_hosts
from threading import Thread
import driver
import time

class LoadBalancer(Thread):
    
    def __init__(self, model):
        self.model = model
    
    def balance(self, node):
        pass
    
    def forecast(self, node):
        pass
        #import statsmodels.api as sm
        #import statsmodels as sm2
        #data =range(20)
        #print sm.tsa
        #
        #sm2.tsa.ar_model.AR
        #
        #model = sm2.tsa.ar_model.AR(data).fit()
        #data = model.predict(len(data)-5,len(data)+10)
        #for i in data:
        #    print i
        #
    
    def run(self):
        while True:
            time.sleep(5)
            print 'running load balancer...'
            
            ## HOTSPOT DETECTOR ########################
            for node in get_hosts():
                # Check past readings
                readings = node.get_readings()
                overload = True
                underload = True
                
                size = len(readings)
                for i in xrange(size - 5, size):
                    overload &= readings[i] > 80
                    underload &= readings[i] < 20
                
                # Check prediction
                #overload &= node.predict() > 75
                #underload &= node.predict() < 10

                # Update overload                                
                node.overloaded = overload
                node.underloaded = underload
                
            ## MIGRATION MANAGER #######################
            # Calculate volumes of each node
            nodes = []
            domains = []
            for node in get_hosts():
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
                
                if node.underloaded: 
                    # print 'Underload: %s' % node.name
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
                
                if node.overloaded:
                    # print 'Overload: %s' % node.name
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
    node = Node('srv0')
    node.add_domain(Domain('target0'))
    node.add_domain(Domain('target1'))
    
    node = Node('srv1')
    node.add_domain(Domain('target2'))
    node.add_domain(Domain('target3'))
    
    node = Node('srv2')
    node = Node('srv3')
    node = Node('srv4')


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
        
