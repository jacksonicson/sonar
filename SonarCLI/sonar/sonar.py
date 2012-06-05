from optparse import OptionParser
from collector import CollectService, ManagementService, ttypes
from thrift import Thrift
from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport

def deploy(sensor, file):
    print 'deploying %s to sensor %s ...' % (file, sensor)
    
    
    
    pass


if __name__ == '__main__':
    parser = OptionParser()
    
    parser.add_option("-d", "--deploy", dest="deploy",
                      help="deploy a ZIP file for a sensor", nargs=2)
    
    (options, args) = parser.parse_args()
    
    if options.deploy:
        deploy(options.deploy[0], options.deploy[1])
    
    pass