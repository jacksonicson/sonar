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
 

def deploy_relay(ret, client_list):
    print 'deploying Relay: '
    
    dlist = []
    
    for host in hosts.get_hosts_list():
        print '   %s' % (host)
        d = __launch(client_list, host, 'relay_deploy', wait=True)
        dlist.append(d)
    
    # Wait for all drones to finish and set phase
    dl = defer.DeferredList(dlist)
    dl.addCallback(finished, client_list)


def deploy_phase(client_list):
    print 'deploying Rain driver: '
    
    dlist = []
    
    for host in hosts.get_hosts('deploy'):
        print '   %s' % (host)
        d = __launch(client_list, host, 'rain_deploy', wait=True)
        dlist.append(d)
    
    # Wait for all drones to finish and set phase
    dl = defer.DeferredList(dlist)
    dl.addCallback(finished, client_list)
    
def main():
    # Create drones
    drones.main()
    
    # Add hosts
    hosts.add_host('load0', 'deploy')
    hosts.add_host('load1', 'deploy')
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
    wait.addCallback(deploy_phase)
    
    # Start the Twisted reactor
    reactor.run()

if __name__ == '__main__':
    main()
