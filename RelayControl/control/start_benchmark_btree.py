from twisted.internet import defer, reactor
from behaviorTree import behaviorTree as btree

from balancer import controller
from control import drones, hosts, base
from logs import sonarlog
from rain import RainService
from thrift.protocol import TBinaryProtocol
from thrift.transport import TTwisted
from twisted.internet import defer, reactor
from twisted.internet.protocol import ClientCreator
from workload import profiles
import domains
import math

######################
## CONFIGURATION    ##
######################
INIT_DB = True
start = False
######################

# Setup logging
logger = sonarlog.getLogger('start_benchmark')

class AllocateDomains(btree.Action):
    def action(self):
        # Create drones
        drones.build_all_drones()
        
        # Setup initial allocation
        if start:
            import allocate_domains
            allocate_domains.allocate_domains(True, controller)
        
        # Add host
        for i in xrange(0, 18):
            hosts.add_host('target%i' % i, 'target')
            hosts.add_host('target%i' % i, 'database')
        
        hosts.add_host('load0', 'load')
        hosts.add_host('load1', 'load')
        
        # Connect with all drone relays
        hosts_map = hosts.get_hosts_list()
        dlist = base.connect(hosts_map)
            
        # Wait for all connections
        wait = defer.DeferredList(dlist)
        wait.addErrback(errback)
        
        # Start the Twisted reactor
        reactor.run()


def errback(failure):
    print 'Error while executing'
    print failure
    reactor.stop()

def finished():
    print 'Startup finished'

def main():
    # Blackboard
    bb = btree.BlackBoard()
    
    # Behavior tree
    root = btree.Sequence(bb);
    root.add(AllocateDomains())
    
    # Execute behavior trees
    defer = root.execute()     
    defer.addCallback(finished)
    
    # Start the Twisted reactor
    reactor.run()

if __name__ == '__main__':
    sonarlog.connect()
    main()
    
