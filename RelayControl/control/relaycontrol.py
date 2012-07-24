from thrift import Thrift, Thrift
from thrift.protocol import TBinaryProtocol, TBinaryProtocol
from thrift.transport import TSocket, TTransport, TTwisted
from twisted.internet import defer, reactor
from twisted.internet.defer import inlineCallbacks
from twisted.internet.protocol import ClientCreator

from control import drones
from control import hosts
from relay import RelayService

# Port the relay service is listening on
PORT = 7900


def __client(client_list, host):
    return client_list[hosts.get_index(host)][1]


def __launch(client_list, host, droneName):
    drone = drones.load_drone(droneName)
    d = __client(client_list, host).launch(drone.data, drone.name)
    return d


def finished(done):
    print "execution successful"
    reactor.stop()


def phase_start_rain(ret, client_list):
    print 'starting rain driver...'
    
    d = __launch(client_list, 'load1', 'rain_start')
    
    dl = defer.DeferredList([d])
    dl.addCallback(finished)


def shutdown_glassfish_rain(client_list):
    print "stopping glassfish and rain drivers..."
    
    dlist = []
    
    d = __launch(client_list, 'playground', 'glassfish_stop')
    dlist.append(d)
    
    d = __launch(client_list, 'load1', 'rain_stop')
    dlist.append(d)
    
    dl = defer.DeferredList(dlist)
    dl.addCallback(finished)
    

def phase_start_glassfish_database(client_list):
    """
    Rain has to be started after Glassfish is running! This is important because 
    the Rain Tracks of the SpecJ driver are accessing the Glassfish services. 
    """
    print 'starting glassfish and database...'
    
    dlist = []
    
    d = __launch(client_list, 'playground', 'glassfish_start')
    dlist.append(d)
    
    d = __launch(client_list, 'playground', 'glassfish_wait')
    dlist.append(d)
    
    d = __launch(client_list, 'playdb', 'spec_dbload')
    dlist.append(d)
    
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
