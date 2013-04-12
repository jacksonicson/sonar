'''
Test program for the IaaS service
'''
from iaas import Infrastructure
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from thrift.transport import TSocket, TTransport
import configuration as config

def main():
    print 'Connecting...'
    transport = TSocket.TSocket(config.IAAS_INTERFACE_IPV4, config.IAAS_PORT)
    transport.open()
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = Infrastructure.Client(protocol)
    
    print 'allocating domain...'
    # hostname = client.allocateDomain()
    # print 'hostname: %s' % hostname
    client.deleteDomain('target100')

if __name__ == '__main__':
    main()
    
