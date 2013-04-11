from twisted.internet import defer, reactor
import drones
import hosts
import base

def finished(done, client_list):
    print "execution successful: %s" % (done)
    reactor.stop()

def deploy_phase(client_list):
    print 'deploying SensorHub: '
    
    dlist = []
    
    # Deploy sensorhubs
    for host in hosts.get_hosts('deploy'):
        print '   %s' % (host)
        d = base.launch(client_list, host, 'sensorhub_deploy', wait=True)
        dlist.append(d)
    
    # Wait for all drones to finish and set phase
    dl = defer.DeferredList(dlist)
    dl.addCallback(finished, client_list)
    
def main():
    # Create drones
    drones.main()
    
    ######################################################
    ## DOMAINS CONFIGURATION                            ##
    ######################################################
#    for i in xrange(0, 18):
#        hosts.add_host('target%i' % i, 'deploy')
#    for i in xrange(0,6):
#        hosts.add_host('srv%i' % i, 'deploy')
#    hosts.add_host('storage0', 'deploy')
#    hosts.add_host('storage1', 'deploy')
#    hosts.add_host('monitor0', 'deploy')
#    hosts.add_host('monitor1', 'deploy')
#    hosts.add_host('load0', 'deploy')
#    hosts.add_host('load1', 'deploy')
#    hosts.add_host('test0', 'deploy')
#    hosts.add_host('test1', 'deploy')
#    hosts.add_host('vmt', 'deploy')
    ######################################################
    
    # Connect
    hosts_map = hosts.get_hosts_list()
    dlist = base.connect(hosts_map)
        
    # Wait for all connections
    wait = defer.DeferredList(dlist)
    wait.addCallback(deploy_phase)
    
    # Start the Twisted reactor
    reactor.run()

if __name__ == '__main__':
    main()
