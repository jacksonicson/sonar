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

# Port the relay service is listening on
PORT = 7900


def __client(client_list, host):
    return client_list[hosts.get_index(host)][1]


def __launch(client_list, host, droneName, wait=True):
    try:
        drone = drones.load_drone(droneName)
        if wait:
            print 'launching: %s' % (drone.name)
            d = __client(client_list, host).launch(drone.data, drone.name)
            return d
        else:
            print 'launching (no wait): %s' % (droneName)
            d = __client(client_list, host).launchNoWait(drone.data, drone.name)            
            return d
    except Exception, e:
        print 'error %s' % (e)


def __poll_for_message(client_list, host, droneName, message):
    try:
        print 'launching (poll for message): %s' % (droneName)
        drone = drones.load_drone(droneName)
        d = __client(client_list, host).pollForMessage(drone.data, drone.name, message)
        return d
    except Exception, e:
        print 'error %s' % (e)


def __wait_for_message(client_list, host, droneName, message, out=None):
    try:
        print 'launching (wait for message): %s' % (droneName)
        drone = drones.load_drone(droneName)
        d = __client(client_list, host).waitForMessage(drone.data, drone.name, message, out)
        return d
    except Exception, e:
        print 'error %s' % (e)


def finished(done, client_list):
    print "execution successful"
    reactor.stop()


def rain_started(ret, rain_client, client_list):
    print 'rain benchmark started'
    finished(ret, client_list)


def rain_connected(rain_client, client_list):
    print 'connected with rain'
    d = rain_client.startBenchmark(long(datetime.now()))
    d.addCallback(rain_started, rain_client, client_list)
    

def trigger_rain_benchmark(ret, client_list):
    print 'connecting with rain'
    creator = ClientCreator(reactor,
                          TTwisted.ThriftClientProtocol,
                          RainService.Client,
                          TBinaryProtocol.TBinaryProtocolFactory(),
                          ).connectTCP('load1', 7852)
                          
    creator.addCallback(lambda conn: conn.client)
    creator.addCallback(rain_connected, client_list)


def phase_start_rain(ret, client_list):
    print 'starting rain driver...'
    
    d = __wait_for_message(client_list, 'load1', 'rain_start', 'Waiting for start signal...', '/opt/rain/rain.log')
    
    dl = defer.DeferredList([d])
    dl.addCallback(trigger_rain_benchmark, client_list)


def shutdown_glassfish_rain(client_list):
    print "stopping glassfish and rain drivers..."
    
    dlist = []
    
    d = __launch(client_list, 'playground', 'glassfish_stop')
    dlist.append(d)
    
    d = __launch(client_list, 'load1', 'rain_stop')
    dlist.append(d)
    
    dl = defer.DeferredList(dlist)
    dl.addCallback(finished, client_list)
    

def phase_start_glassfish_database(client_list):
    """
    Rain has to be started after Glassfish is running! This is important because 
    the Rain Tracks of the SpecJ driver are accessing the Glassfish services. 
    """
    print 'starting glassfish and database...'
    
    dlist = []
    
    d = __launch(client_list, 'playground', 'glassfish_start', wait=False)
    dlist.append(d)
    
    d = __poll_for_message(client_list, 'playground', 'glassfish_wait', 'domain1 running')
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
    start = True
    if start:
        print 'starting system ...'
        wait.addCallback(start_phase)
        # wait.addCallback(phase_start_rain)
    else:
        print 'stopping system ...'
        wait.addCallback(stop_phase)
    
    # Start the Twisted reactor
    reactor.run()

if __name__ == '__main__':
    main()
