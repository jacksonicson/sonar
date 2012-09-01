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
    
#    hosts.add_host('srv0', 'deploy')
#    hosts.add_host('srv1', 'deploy')
#    hosts.add_host('srv2', 'deploy')
#    hosts.add_host('srv3', 'deploy')
#    hosts.add_host('srv4', 'deploy')
#    hosts.add_host('srv5', 'deploy')
#    
#    hosts.add_host('load0', 'deploy')
#    hosts.add_host('load1', 'deploy')
#    
#    hosts.add_host('monitor0', 'deploy')
#    hosts.add_host('monitor1', 'deploy')
#    
#    hosts.add_host('storage0', 'deploy')
#    hosts.add_host('storage1', 'deploy')

    # Add VMs
#    hosts.add_host('glassfish0', 'deploy')
#    hosts.add_host('glassfish1', 'deploy')
#    hosts.add_host('glassfish2', 'deploy')
#    hosts.add_host('glassfish3', 'deploy')
#    hosts.add_host('glassfish4', 'deploy')
#    hosts.add_host('glassfish5', 'deploy')
#    hosts.add_host('mysql0', 'deploy')
#    hosts.add_host('mysql1', 'deploy')
#    hosts.add_host('mysql2', 'deploy')
#    hosts.add_host('mysql3', 'deploy')
#    hosts.add_host('mysql4', 'deploy')
#    hosts.add_host('mysql5', 'deploy')
#    hosts.add_host('target0', 'deploy')
    hosts.add_host('target1', 'deploy')
    hosts.add_host('target2', 'deploy')
    hosts.add_host('target3', 'deploy')
    
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
