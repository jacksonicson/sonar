'''
Test program for the IaaS service
'''
from iaas import Infrastructure
from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket
import configuration as config

def main():
    print 'TEST Connecting...'
    transport = TSocket.TSocket(config.IAAS_INTERFACE_IPV4, config.IAAS_PORT)
    transport.open()
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = Infrastructure.Client(protocol)
    
#    print 'allocating domain...'
#    hostname = client.allocateDomain()
#    print 'hostname: %s' % hostname
#
#    while client.isDomainReady(hostname) == False:
#        print 'Waiting for domain...'
#        time.sleep(5) 
#    
#    print 'Deleting domain'
#    hostname = 'target102'
#    client.deleteDomain(hostname)

    client.launchDrone('glassfish', 'target100')

if __name__ == '__main__':
    main()
    
