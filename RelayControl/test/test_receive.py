'''
Test: Connect with Sonar Collector and receive metrics of some servers/VMs
'''

from collector import NotificationClient, NotificationService, ttypes
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from thrift.transport import TSocket, TTransport
import configuration as config
import threading

class ServiceThread(threading.Thread):
    def __init__(self, handler):
        threading.Thread.__init__(self)
        
        # Mark this one as a daemon so it can be killed by python
        self.setDaemon(True)
        
        self.handler = handler
        
    def run(self):
        processor = NotificationClient.Processor(self.handler)
        transport = TSocket.TServerSocket(host=config.LISTENING_INTERFACE_IPV4, port=config.LISTENING_PORT)
        
        tfactory = TTransport.TBufferedTransportFactory()
        pfactory = TBinaryProtocol.TBinaryProtocolFactory()
        
        # Launch the server
        server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
        
        print 'Starting TSD receiver service...'
        server.serve()
        

def connect_sonar(filters, handler, interface=config.LISTENING_INTERFACE_IPV4, collector=config.COLLECTOR_HOST):
    print 'Connecting with Sonar ...'

    # Start the Receiver    
    receiver = ServiceThread(handler)
    receiver.start()
    
    # Register the Receiver in the Controller
    # Make socket
    transport = TSocket.TSocket(collector, config.COLLECTOR_PORT)
    
    # Buffering is critical. Raw sockets are very slow
    transport = TTransport.TBufferedTransport(transport)
    
    # Wrap in a protocol
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    
    # Create a client to use the protocol encoder
    serviceClient = NotificationService.Client(protocol)
    
    # Connect!
    transport.open()
    
    # Subscribe
    print 'Subscribing now...'
    serviceClient.subscribe(interface, config.LISTENING_PORT, filters)
    
    return receiver
    

class Handler(NotificationClient.Iface):
    def receive(self, datalist):
        for data in datalist:
            reading = data.reading
            ident = data.id
            print '%s - %s = %s' % (reading.value, ident.hostname, ident.sensor)
        

if __name__ == '__main__':
    print 'Starting...'
    
    # Called if a new reading arrives
    handler = Handler()
    
    # Define hosts and sensors to listen on
    filters = [
               ttypes.SensorToWatch('srv0', 'psutilcpu'),
               ttypes.SensorToWatch('srv1', 'psutilcpu'),
               ttypes.SensorToWatch('srv1', 'psutilmem.phymem'),
               ]
    
    thread = connect_sonar(filters, handler)
    thread.join()
    
    
    