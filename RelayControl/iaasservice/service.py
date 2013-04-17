'''
Provides a service to control the infrastructure like an
IaaS service 
'''

from iaas import Infrastructure
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from thrift.transport import TSocket, TTransport
from virtual import clone
import configuration as config
import threading
import behaviors


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
        self.counter = 100
    
    def allocateDomain(self):
        print 'allocating domain now...'
        name = 'target%i' % self.counter
        clone.clone('playglassdb_v2', name, self.counter)
        self.counter += 1
        return name
    
    def isDomainReady(self, hostname):
        print 'checking domain state...'
        return clone.try_connecting(hostname)
    
    def deleteDomain(self, hostname):
        print 'deleting domain now...'
        clone.delete(hostname)
        return True
    
    def launchDrone(self, drone, hostname):
        print 'Launching btree %s on host %s ...' % (drone, hostname)
        btree = behaviors.StartGlassfishTree(hostname)
        btree.launch()
        return True


def start():
    print 'Starting twisted reactor...'
    clone.start()
    
    print 'Creating IaaS handler...'
    handler = Handler()
    
    print 'Starting IaaS service in main thread...'
    global thread
    thread = ServiceThread(handler)
    
    # Blocks until the service is disrupted (e.g. by SIGTERM)
    thread.run()
    
    print 'Stopping reactor...'
    clone.stop()
