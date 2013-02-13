from collector import NotificationClient
from collector import ttypes
from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport

def main():
    print 'Starting Test Client...'

    # Make socket
    transport = TSocket.TSocket('localhost', 9876)
    
    # Buffering is critical. Raw sockets are very slow
    transport = TTransport.TBufferedTransport(transport)
    
    # Wrap in a protocol
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    
    # Create a client to use the protocol encoder
    serviceClient = NotificationClient.Client(protocol)
    
    # Connect!
    transport.open()

    # Action
    dd = ttypes.NotificationData()
    
    ident = ttypes.Identifier()
    ident.timestamp = 342343
    ident.sensor = 'test'
    ident.hostname = 'tes'
    
    dd.id = ident
    
    reading = ttypes.MetricReading()
    reading.labels = ['asdf']
    reading.value = float(2.0)
    
    dd.reading = reading

    sef = []
    serviceClient.receive(sef)
    
    # Finish
    transport.close()
    

if __name__ == '__main__':
    main()
