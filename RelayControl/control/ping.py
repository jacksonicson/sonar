import drones, hosts, base
from datetime import datetime
from rain import RainService, constants, ttypes
from relay import RelayService
from string import Template
from thrift import Thrift, Thrift
from thrift.protocol import TBinaryProtocol, TBinaryProtocol
from thrift.transport import TSocket, TTransport, TTwisted
from twisted.internet import defer, reactor
from twisted.internet.defer import inlineCallbacks
from twisted.internet.protocol import ClientCreator

def finished(done, client_list):
    print "execution successful %s" % done
    reactor.stop()

def start_phase(client_list):
    print 'All Systems alive!'
    finished(client_list, client_list)
    
def main():
    # Create drones
    drones.main()
    
    # Add hosts
    for i in xrange(0, 18):
        hosts.add_host('target%i' % i, 'action')
        
    hosts_map = hosts.get_hosts_list()
    
    # Connect with all drone relays
    deferList = base.connect(hosts_map)
    wait = defer.DeferredList(deferList)
    
    # Decide what to do after connection setup
    wait.addCallback(start_phase)
    
    # Start the Twisted reactor
    reactor.run()

if __name__ == '__main__':
    main()
