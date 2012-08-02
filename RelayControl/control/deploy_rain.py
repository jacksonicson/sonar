import drones, hosts, base
from twisted.internet import defer, reactor

def finished(done, client_list):
    print "execution successful"
    reactor.stop()
 
 
def deploy_phase(client_list):
    print 'deploying rain driver...'
    
    dlist = []
    
    for host in hosts.get_hosts('deploy'):
        print '   %s' % (host)
        d = base.launch(client_list, host, 'rain_deploy', wait=True)
        dlist.append(d)
    
    # Wait for all drones to finish and set phase
    dl = defer.DeferredList(dlist)
    dl.addCallback(finished, client_list)
    
    
def main():
    # Create drones
    drones.main()
    
    # Add hosts
    hosts.add_host('playground', 'deploy')
    
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
