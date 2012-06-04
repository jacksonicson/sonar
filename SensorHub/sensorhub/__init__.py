from collector import ManagementService


from thrift import Thrift
from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport
import sys


def main():
    print "test"
    
    # Make socket
    transport = TSocket.TSocket('localhost', 7931)
    
    # Buffering is critical. Raw sockets are very slow
    transport = TTransport.TBufferedTransport(transport)
    
    # Wrap in a protocol
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    
    client = ManagementService.Client(protocol); 
    
    transport.open(); 
    
    list = client.getSensorLabels("cpu");
    print "Sensor labels"
    for i in list:
        print i
    


if __name__ == '__main__':
    main(); 
