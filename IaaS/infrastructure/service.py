'''
Provides a service to control the infrastructure like an
IaaS service 
'''

from iaas import Infrastructure
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from thrift.transport import TSocket, TTransport
import configuration as config
import threading
#from virtual import clone


class ServiceThread(threading.Thread):
    def __init__(self, handler):
        threading.Thread.__init__(self)
        
        # Mark this one as a daemon so it can be killed by python
        self.setDaemon(True)
        
        self.handler = handler
        
    def run(self):
        print self.handler
        processor = Infrastructure.Processor(self.handler)
        transport = TSocket.TServerSocket(host=config.IAAS_INTERFACE_IPV4, port=config.IAAS_PORT)
        
        tfactory = TTransport.TBufferedTransportFactory()
        pfactory = TBinaryProtocol.TBinaryProtocolFactory()
        
        # Launch the server
        server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
        
        print 'Running IaaS service...'
        server.serve()

class Handler(Infrastructure.Iface):
    def __init__(self):
        pass
    
    def allocateDomain(self):
        print 'allocating domain now...'
        return 'test'
    
    def isDomainReady(self, hostname):
        pass
    
    def deleteDomain(self, hostname):
        pass


def start():
    print 'Creating IaaS handler...'
    handler = Handler()
    
    print 'Starting IaaS service thread...'
    thread = ServiceThread(handler)
    thread.start()
    thread.join()
