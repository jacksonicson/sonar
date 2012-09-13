from twisted.internet import defer, reactor
import base
import drones
import hosts

def finished(done, client_list):
    print "execution successful: %s" % (done)
    reactor.stop()


def error(done, client_list):
    # If relay gets restarted the connection to relay is broken
    # So, it is expected that an error occurs, no logging here. 
    pass


def deploy_phase(client_list):
    print 'deploying rain driver...'
    
    dlist = []
    
    for host in hosts.get_hosts('deploy'):
        print '   %s' % (host)
        d = base.launch(client_list, host, 'relay_deploy', wait=True)
        dlist.append(d)
        d.addErrback(error, client_list)
    
    # Wait for all drones to finish and set phase
    dl = defer.DeferredList(dlist)
    dl.addCallback(finished, client_list)
    
    
def main():
    # Create drones
    drones.main()
    
    # Add hosts
    for i in xrange(0, 9):
        hosts.add_host('target%i' % i, 'deploy')
    
    # Connect with all drone relays
    hosts_map = hosts.get_hosts_list()
    dlist = base.connect(hosts_map)
        
    # Wait for all connections
    wait = defer.DeferredList(dlist)
    wait.addCallback(deploy_phase)
    
    # Start the Twisted reactor
    reactor.run()

if __name__ == '__main__':
    main()
