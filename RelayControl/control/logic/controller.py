
from collector import NotificationClient, NotificationService, ttypes
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from thrift.transport import TSocket, TTransport
import threading

################################
## Configuration              ##
LISTENING_PORT = 9876
LISTENING_INTERFACE_IPV4 = '192.168.96.3'

COLLECTOR_PORT = 7911
COLLECTOR_HOST = 'monitor0.dfg'
################################


class NotificationReceiverImpl:
    
    def receive(self, data):
        print 'receiving notification data'
        print data
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
    client = ServiceThread()
    client.start()
    
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
    client.join(); 
    

if __name__ == '__main__':
    main()
