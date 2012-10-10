
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
        self.overloaded = False
        
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
    


class LoadBalancer(Thread):
    
    def balance(self, node):
        pass
    
    def run(self):
        while True:
            print 'running load balancer...'
            
            # Hotspot detector
            for node in hosts.values():
                # Check past readings
                readings = node.get_readings()
                overload = True
                
                size = len(readings)
                for i in xrange(size - 5, size):
                    overload &= readings[i] > 75
                
                # Check prediction
                overload &= node.predict() > 75

                # Update overload                                
                node.overloaded = overload
                
            # Migration manager
            # Calculate volumes of each node
            nodes = []
            domains = []
            for node in hosts.values():
                volume = 1.0 / (1.0 - node.mean_load())
                node.volume = volume
                print volume
                node.volume_size = volume / 8.0 # 8 GByte
                
                if node.type == types.NODE:
                    nodes.append(node)
                elif node.type == types.DOMAIN: 
                    domains.append(node)
                
            # Sort nodes to their volume in reverse order
            nodes.sort(lambda a, b: int(a.volume - b.volume))
            
            # Sort domains to their volume_size in reverse order
            domains.sort(lambda a, b: int(a.volume_size - b.volume_size))
            
            for node in nodes:
                print 'node %s :: %s' % (node.name, node.volume) 
                 
            
            
            
            time.sleep(2)

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
    
def test():
    pass

class Driver(Thread):
    # Use the existing profiles to load TSD from Times
    from workload import profiles, util
    from service import times_client
    
    print 'Connecting with Times'
    connection = times_client.connect()
    
    tsd = []
    for service in profiles.selected: 
        service = service.name + profiles.POSTFIX_NORM
        print 'loading service: %s' % (service)
        ts = connection.load(service)
        tsd.append(util.to_array(ts))
    
    
    
    def run(self):
        for i in xrange(0, 100):
            for node in hosts.values():
                data = ttypes.NotificationData()
                data.id = ttypes.Identifier()  
                data.id.hostname = node.name
                data.id.sensor = 'psutilcpu'
                data.id.timestamp = i
                
                data.reading = ttypes.MetricReading()
                data.reading.value = float(i) / 100.0
                data.reading.labels = []
                
                notification.receive(data)
            
            time.sleep(2)

if __name__ == '__main__':
    # main()
    notification = NotificationReceiverImpl()
    
    balancer = LoadBalancer()
    balancer.start()
    
    # Build internal infrastructure representation
    node = Node('srv0')
    node.add_domain(Domain('target0'))
    node.add_domain(Domain('target1'))
    
    node = Node('srv1')
    node.add_domain(Domain('target2'))
    node.add_domain(Domain('target3'))
    
    # Start the driver thread which simulates Sonar
    driver = Driver()
    driver.start() 
        
