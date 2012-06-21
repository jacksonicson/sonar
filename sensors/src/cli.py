from optparse import OptionParser
from collector import CollectService, ManagementService, ttypes
from thrift import Thrift
from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport

def deploy(name, zipfile):
    print 'deploying %s to sensor %s ...' % (zipfile, name)
    
    # Make socket
    transport = TSocket.TSocket('131.159.41.171', 7931)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = ManagementService.Client(protocol);
    transport.open();
    
    f = open(zipfile, 'rb')
    ba = f.read()
    f.close()
    
    client.deploySensor(name, ba); 
    
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