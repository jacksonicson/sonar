from optparse import OptionParser
from collector import CollectService, ManagementService, ttypes
from thrift import Thrift
from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport

def deploy(sensor, file):
    print 'deploying %s to sensor %s ...' % (file, sensor)
    
    # Make socket
    transport = TSocket.TSocket('localhost', 7931)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = ManagementService.Client(protocol);
    transport.open();
    
    
    
    f = open(file, 'rb')
    ba = bytearray()
    byte = f.read(1)
    while byte:
        ba.extend(byte)
        byte = f.read(1)
    f.close()
    
    client.deploySensor(sensor, ba); 
    
    transport.close();
    print 'finished' 
    
    pass


if __name__ == '__main__':
    parser = OptionParser()
    
    parser.add_option("-d", "--deploy", dest="deploy",
                      help="deploy a ZIP file for a sensor", nargs=2)
    
    (options, args) = parser.parse_args()
    
    if options.deploy:
        deploy(options.deploy[0], options.deploy[1])
    
    pass