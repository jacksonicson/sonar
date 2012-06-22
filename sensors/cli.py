from optparse import OptionParser
from collector import ttypes
import connect

def deploy(name, zipfile):
    print 'deploying %s to sensor %s ...' % (zipfile, name),
    
    # Read file 
    f = open(zipfile, 'rb')
    ba = f.read()
    f.close()

    # Deploy sensor
    transport, client = connect.openClient()    
    client.deploySensor(name, ba); 
    connect.closeClient(transport)
    
    print '[OK]'
    
if __name__ == '__main__':
    parser = OptionParser()
    
    parser.add_option("-d", "--deploy", dest="deploy",
                      help="deploy a ZIP file for a sensor", nargs=2)
    
    (options, args) = parser.parse_args()
    
    if options.deploy:
        deploy(options.deploy[0], options.deploy[1])
    
    pass