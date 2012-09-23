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
    dlist = []
    for host in hosts.get_hosts('action'):
        print '   %s' % (host)
        
        d = base.launch(client_list, host, 'test', wait=False)
        dlist.append(d)
        
#        d = base.launch(client_list, host, 'test', wait=True)
#        dlist.append(d)

        base.client(client_list, host).isAlive(234433)
        # base.client(client_list, host).kill(234433)

#        base.poll_for_message(client_list, host, 'test', 'done')
        
#        base.wait_for_message(client_list, host, 'test', 'done')
    
    dl = defer.DeferredList(dlist)  
    dl.addCallback(finished, client_list)
    
def main():
    # Create drones
    drones.main()
    
    # Add hosts
    hosts.add_host('192.168.96.6', 'action')
        
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
