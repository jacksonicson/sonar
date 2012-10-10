
from collector import NotificationClient, NotificationService, ttypes
from threading import Thread
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from thrift.transport import TSocket, TTransport
import numpy as np
import threading
import time

################################
## Configuration              ##
LISTENING_PORT = 9876
LISTENING_INTERFACE_IPV4 = '192.168.96.3'

COLLECTOR_PORT = 7911
COLLECTOR_HOST = 'monitor0.dfg'
################################

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

types = enum('NODE', 'DOMAIN')

hosts = {}
class Host(object):
    LENGTH = 10 # last n measurements
    
    def __init__(self):
        self.readings = [0 for _ in xrange(0, Host.LENGTH)]
        self.counter = 0
        self.volume = 0
        self.overloaded = False
        self.underloaded = False
        
        self.blocked = 0
        
    def put(self, reading):
        self.readings[self.counter] = reading.value
        self.counter = (self.counter + 1) % Host.LENGTH
        
    def mean_load(self):
        return np.mean(self.readings)
    
    def get_readings(self):
        index = (self.counter) % Host.LENGTH
        result = []
        for _ in xrange(Host.LENGTH):
            result.append(self.readings[index])
            index = (index + 1) % Host.LENGTH
            
        return result
    
    def predict(self):
        return 100
    
    def handle_overload(self):
        pass
        
    
class Domain(Host):
    def __init__(self, name):
        super(Domain, self).__init__()
        hosts[name] = self
        
        self.name = name
        self.type = types.DOMAIN
        self.ts = None
        
    def get_watch_filter(self):
        return ttypes.SensorToWatch(self.name, 'psutilcpu')
    


class Node(Host):
    def __init__(self, name):
        super(Node, self).__init__()
        hosts[name] = self
        
        self.name = name
        self.domains = {}
        self.type = types.NODE
    
    def add_domain(self, domain):
        self.domains[domain.name] = domain
        
    def get_watch_filter(self):
        return ttypes.SensorToWatch(self.name, 'psutilcpu')
    
    def dump(self):
        domains = ', '.join(self.domains.keys())
        print 'Host: %s Load: %f Volume: %f Domains: %s' % (self.name, self.mean_load(), self.volume, domains)
    

class LoadBalancer(Thread):
    
    def balance(self, node):
        pass
    
    def run(self):
        while True:
            time.sleep(5)
            print 'running load balancer...'
            
            ## HOTSPOT DETECTOR ########################
            for node in hosts.values():
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
            for node in hosts.values():
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
                 
            
            

class NotificationReceiverImpl:
    
    def receive(self, data):
        hostname = data.id.hostname
        
        if hosts.has_key(hostname):
            host = hosts[hostname]
        else:
            return
        
        host.put(data.reading)
        return


class ServiceThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        handler = NotificationReceiverImpl()
        processor = NotificationClient.Processor(handler)
        transport = TSocket.TServerSocket(host=LISTENING_INTERFACE_IPV4, port=LISTENING_PORT)
        
        tfactory = TTransport.TBufferedTransportFactory()
        pfactory = TBinaryProtocol.TBinaryProtocolFactory()
        
        server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
        print 'Starting TSD callback service...'
        server.serve()
        

def main(interface=LISTENING_INTERFACE_IPV4, collector=COLLECTOR_HOST):
    print 'Starting Controller...'

    # Start the Receiver    
    receiver = ServiceThread()
    receiver.start()
    
    # Register the Receiver in the Controller
    # Make socket
    transport = TSocket.TSocket(collector, COLLECTOR_PORT)
    
    # Buffering is critical. Raw sockets are very slow
    transport = TTransport.TBufferedTransport(transport)
    
    # Wrap in a protocol
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    
    # Create a client to use the protocol encoder
    serviceClient = NotificationService.Client(protocol)
    
    # Connect!
    transport.open()

    # Define hosts and sensors to listen on
    srv0_cpu = ttypes.SensorToWatch('srv0', 'psutilcpu')
    glassfish0_cpu = ttypes.SensorToWatch('glassfish0', 'psutilcpu')

    # Subscribe
    print 'Subscribing now...'
    serviceClient.subscribe(interface, LISTENING_PORT, [srv0_cpu, glassfish0_cpu]),
    print 'Done'

    # Wait for join
    print 'Waiting for exit...'
    receiver.join(); 
    
    
class Driver(Thread):
        
    def run(self):
        # Use the existing profiles to load TSD from Times
        from workload import profiles, util
        from service import times_client
        
        print 'Connecting with Times'
        connection = times_client.connect()
        
        i = 0
        length = 0
        for host in hosts.values():
            if host.type != types.DOMAIN:
                continue
           
            service = profiles.selected[i]
            i += 1
            
            load = service.name + profiles.POSTFIX_NORM
            print 'loading service: %s ...' % (load)
            ts = connection.load(load)
            ts = util.to_array(ts)[1] # only load time
            host.ts = ts
            length = max(length, len(ts))
        
        # Simulate time steps
        while True: 
            for tindex in xrange(length):
                for host in hosts.values():
                    if host.type != types.NODE:
                        continue
                    
                    aggregated_load = 0
                    for domain in host.domains.values():
                        load = domain.ts[tindex]
                        aggregated_load += load 
                    
                        data = ttypes.NotificationData()
                        data.id = ttypes.Identifier()  
                        data.id.hostname = domain.name
                        data.id.sensor = 'psutilcpu'
                        data.id.timestamp = tindex
                        
                        data.reading = ttypes.MetricReading()
                        data.reading.value = load
                        data.reading.labels = []
                        
                        notification.receive(data)
                        
                    # print 'aggregated: %s = %f' % (host.name, aggregated_load)
                    data = ttypes.NotificationData()
                    data.id = ttypes.Identifier()  
                    data.id.hostname = host.name
                    data.id.sensor = 'psutilcpu'
                    data.id.timestamp = tindex
                    
                    data.reading = ttypes.MetricReading()
                    data.reading.value = aggregated_load
                    data.reading.labels = []
                    
                    notification.receive(data) 
                
                time.sleep(1)
            
            print 'NEXT SIMULATION CYCLE #########################################'
        

if __name__ == '__main__':
    notification = NotificationReceiverImpl()
    
    # Build internal infrastructure representation
    node = Node('srv0')
    node.add_domain(Domain('target0'))
    node.add_domain(Domain('target1'))
    
    node = Node('srv1')
    node.add_domain(Domain('target2'))
    node.add_domain(Domain('target3'))
    
    node = Node('srv2')
    node = Node('srv3')
    node = Node('srv4')
    
    # Start the driver thread which simulates Sonar
    driver = Driver()
    driver.start()
    
    # Start load balancer thread which detects hotspots and triggers migrations
    balancer = LoadBalancer()
    balancer.start() 
        
