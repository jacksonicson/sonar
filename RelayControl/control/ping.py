from control import drones, hosts
from datetime import datetime
from rain import RainService, constants, ttypes
from relay import RelayService
from thrift import Thrift, Thrift
from thrift.protocol import TBinaryProtocol, TBinaryProtocol
from thrift.transport import TSocket, TTransport, TTwisted
from twisted.internet import defer, reactor
from twisted.internet.defer import inlineCallbacks
from twisted.internet.protocol import ClientCreator
from string import Template

# Port the relay service is listening on
PORT = 7900

def finished(done, client_list):
    print "execution successful"
    reactor.stop()

def start_phase(client_list):
    print 'All Systems alive!'
    finished(None, client_list)
    
def stop_phase(client_list):
    print 'All Systems alive!'
    finished(None, client_list)
    
    
def main():
    # Create drones
    drones.main()
    
    # Add hosts
    hosts.add_host('monitor0', 'node')
    hosts.add_host('monitor1', 'node')
    hosts.add_host('storage0', 'node')
    hosts.add_host('storage1', 'node')
    hosts.add_host('load0', 'node')
    hosts.add_host('load1', 'node')
    hosts.add_host('srv0', 'node')
    hosts.add_host('srv1', 'node')
    hosts.add_host('srv2', 'node')
    hosts.add_host('srv3', 'node')
    hosts.add_host('srv4', 'node')
    hosts.add_host('srv5', 'node')
    hosts_map = hosts.get_hosts_list()
    
    # Connect with all drone relays
    dlist = []
    for i in hosts_map:
        print 'Connecting with relay %s:%i ' % (i, PORT)
        
        creator = ClientCreator(reactor,
                          TTwisted.ThriftClientProtocol,
                          RelayService.Client,
                          TBinaryProtocol.TBinaryProtocolFactory(),
                          ).connectTCP(i, PORT)
        creator.addCallback(lambda conn: conn.client)
        
        d = defer.Deferred()
        creator.addCallback(d.callback)
        dlist.append(d)
        
    # Wait for all connections
    wait = defer.DeferredList(dlist)
    
    # Decide what to do after connection setup
    start = True
    if start:
        print 'starting system ...'
        wait.addCallback(start_phase)
        # wait.addCallback(phase_start_rain) # have to change the method signature
    else:
        print 'stopping system ...'
        wait.addCallback(stop_phase)
    
    # Start the Twisted reactor
    reactor.run()

if __name__ == '__main__':
    main()
