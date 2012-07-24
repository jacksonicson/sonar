

from thrift import Thrift, Thrift
from thrift.protocol import TBinaryProtocol, TBinaryProtocol
from thrift.transport import TSocket, TTransport, TTwisted
from twisted.internet import defer, reactor
from twisted.internet.defer import inlineCallbacks
from twisted.internet.protocol import ClientCreator
import os

from control import drones
from control import hosts
from relay import RelayService

PORT = 7900

def done_all(done):
    print "execution successful"
    reactor.stop()

def phase_start_rain(ret, client_list):
    print 'starting rain driver...'
    
    d = defer.Deferred()
    drone_rain_start = drones.load_drone('rain_start')
    client_list[2][1].launch(drone_rain_start, 'rain_start').addCallback(d.callback)
    
    dl = defer.DeferredList([d])
    dl.addCallback(done_all)


def shutdown_glassfish_rain(client_list):
    print "stopping glassfish and rain drivers..."
    
    drone_glassfish_stop = drones.load_drone('glassfish_stop')
    drone_rain_stop = drones.load_drone('rain_stop')
    
    dlist = []
    
    d = defer.Deferred()
    dlist.append(d)
    client_list[0][1].launch(drone_glassfish_stop, 'glassfish_stop').addCallback(d.callback)
    
    d = defer.Deferred()
    dlist.append(d)
    client_list[hosts.get_index('load1')][1].launch(drone_rain_stop, 'rain_stop').addCallback(d.callback)
    
    dl = defer.DeferredList(dlist)
    dl.addCallback(done_all)
    

def phase_start_glassfish_database(client_list):
    """
    Rain has to be started after Glassfish is running! This is important because 
    the Rain Tracks of the SpecJ driver are accessing the Glassfish services. 
    """
    
    print 'starting glassfish and database...'
    
    # Loading drones
    drone_glassfish_start = drones.load_drone('glassfish_start')
    drone_spec_dbload = drones.load_drone('spec_dbload')
    drone_glassfish_wait = drones.load_drone('glassfish_wait')

    # Launch Glassfish and wait for its start
    dlist = []
    d = defer.Deferred()
    dlist.append(d)
    client_list[0][1].launchNoWait(drone_glassfish_start, "glassfish_start").addCallback(d.callback)
    
    d = defer.Deferred()
    dlist.append(d)
    client_list[0][1].pollForMessage(drone_glassfish_wait, "glassfish_wait", "domain1 running").addCallback(d.callback)
    
    d = defer.Deferred()
    dlist.append(d)
    client_list[1][1].launch(drone_spec_dbload, "spec_dbload").addCallback(d.callback)
    
    # Wait for all drones to finish and set phase
    dl = defer.DeferredList(dlist)
    dl.addCallback(phase_start_rain, client_list)
 
 
def start_phase(client_list):
    phase_start_glassfish_database(client_list)
    
    
def stop_phase(client_list):
    shutdown_glassfish_rain(client_list)
    
    
def main():
    # Create drones
    drones.main()
    
    # Add hosts
    hosts.add_host('playground', 'target')
    hosts.add_host('playdb', 'db')
    hosts.add_host('load1', 'driver')
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
    start = False
    if start:
        print 'starting system ...'
        wait.addCallback(start_phase)
    else:
        print 'stopping system ...'
        wait.addCallback(stop_phase)
    
    # Start the Twisted reactor
    reactor.run()


if __name__ == '__main__':
    main()
