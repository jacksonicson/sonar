from collector import NotificationClient, NotificationService, ttypes
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from thrift.transport import TSocket, TTransport
import threading

################################
## Configuration              ##
LISTENING_PORT = 9876
LISTENING_INTERFACE_IPV4 = '192.168.96.6'

COLLECTOR_PORT = 7911
COLLECTOR_HOST = 'monitor0.dfg'
################################


class ServiceThread(threading.Thread):
    def __init__(self, handler):
        threading.Thread.__init__(self)
        
        # Mark this one as a daemon so it can be killed by python
        self.setDaemon(True)
        
        self.handler = handler
        
    def run(self):
        print self.handler
        processor = NotificationClient.Processor(self.handler)
        transport = TSocket.TServerSocket(host=LISTENING_INTERFACE_IPV4, port=LISTENING_PORT)
        
        tfactory = TTransport.TBufferedTransportFactory()
        pfactory = TBinaryProtocol.TBinaryProtocolFactory()
        
        # Launch the server
        server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
        
        print 'Starting TSD callback service...'
        server.serve()
        

def connect_sonar(model, handler, interface=LISTENING_INTERFACE_IPV4, collector=COLLECTOR_HOST):
    print 'Connecting with Sonar ...'

    # Start the Receiver    
    receiver = ServiceThread(handler)
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
    filters = []
    for host in model.get_hosts():
        fi = host.get_watch_filter()
        print fi
        filters.append(fi)

    # Subscribe
    print 'Subscribing now...'
    serviceClient.subscribe(interface, LISTENING_PORT, filters),
    print 'Done'
    