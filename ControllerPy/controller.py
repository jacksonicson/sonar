
from collector import NotificationClient 

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

import threading

LISTENING_PORT = 8000

COLLECTOR_PORT = 7911
COLLECTOR_HOST = 'localhost'

class NotificationServiceImpl(object):
    def receive(self, data):
        print 'receiving notification data'

class NotificationService(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        handler = NotificationServiceImpl()
        processor = NotificationClient.Processor(handler)
        transport = TSocket.TServerSocket(port=LISTENING_PORT)
        tfactory = TTransport.TBufferedTransportFactory()
        pfactory = TBinaryProtocol.TBinaryProtocolFactory()
        
        server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
        print 'Starting TSD callback service...'
        server.serve()

def main():
    print 'Starting Controller...'

    # Start the Receiver    
    client = NotificationService()
    client.start()
    print 'Receiver started'
    
    # Register the Receiver in the Controller


    # Wait for join
    client.join(); 
    
    
    
    
    

if __name__ == '__main__':
    main()