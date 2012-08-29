from control import drones, hosts, base
from logs import sonarlog, sonarlog
from rain import RainService
from thrift.protocol import TBinaryProtocol
from thrift.transport import TTwisted
from twisted.internet import defer, reactor
from twisted.internet.protocol import ClientCreator
from workload import profiles
import domains
import logging
import logic.controller as controller
import math

# Setup logging
logger = sonarlog.getLogger('start_benchmark')

def finished_end(done, client_list):
    print 'finish phase'
    logger.log(sonarlog.SYNC, 'end of shutdown sequence')
    reactor.stop()

def finished(done, client_list):
    print 'finish phase'
    logger.log(sonarlog.SYNC, 'end of startup sequence')
    reactor.stop()

    # Launch the controller
    print '### CONTROLLER ###############################'
    print 'starting controller'
    logger.info('loading controller')
    # controller.main() 


def ramp_up(ret, rain_client, client_list):
    print 'sleeping during ramp-up for %i seconds' % (ret)
    logger.info('sleeping during ramp-up for %i seconds' % (ret))
    reactor.callLater(ret, finished, None, client_list)
    

def rain_started(ret, rain_client, client_list):
    print 'rain is driving load now, waiting for ramp-up finish'
    logger.log(sonarlog.SYNC, 'start driving load')
    logger.info('querying ramp-up duration')
    
    d = rain_client[0][1].getRampUpTime()
    d.addCallback(ramp_up, rain_client, client_list) 


def rain_connected(rain_clients, client_list):
    print 'releasing load...'
    logger.info('releasing load on rain drivers')
    
    dlist = []
    for client in rain_clients:
        print '   * releasing %s' % (client[1])
        logger.debug('releasing')
        
        d = client[1].startBenchmark(long(base.millis()))
        dlist.append(d)
    
    d = defer.DeferredList(dlist)
    d.addCallback(rain_started, rain_clients, client_list)
    

def trigger_rain_benchmark(ret, client_list):
    print 'connecting with rain drivers...'
    logger.info('connecting with rain drivers')
    
    dlist = []
    for driver in hosts.get_hosts('load'):
        print '   * connecting %s' % (driver)
        creator = ClientCreator(reactor,
                              TTwisted.ThriftClientProtocol,
                              RainService.Client,
                              TBinaryProtocol.TBinaryProtocolFactory(),
                              ).connectTCP(driver, 7852)
        creator.addCallback(lambda conn: conn.client)
        dlist.append(creator)
        
    d = defer.DeferredList(dlist)                  
    d.addCallback(rain_connected, client_list)


def phase_start_rain(done, client_list):
    print 'starting rain drivers...'
    logger.info('starting rain drivers')
    
    dlist = []

    targets = hosts.get_hosts('target')
    target_count = len(targets)
    
    drivers = hosts.get_hosts('load')
    driver_count = len(drivers)
    
    targets_per_driver = int(math.ceil(float(target_count) / float(driver_count)))
    
    for i in range(0, driver_count):
        driver = drivers[i]
        
        # Build targets for configuration
        config_targets = []
        for target in targets[i * targets_per_driver : (i + 1) * targets_per_driver]:
            config_target = {}
            config_target['target'] = target
            config_target['profile'] = domains.profile_by_name(target) + profiles.POSTFIX_USER
            config_targets.append(config_target)

        print config_targets
                
        # Configure drone
        drones.prepare_drone('rain_start', 'rain.config.specj.json', targets=config_targets)
        drones.create_drone('rain_start')
        
        # Launch this drone
        d = base.wait_for_message(client_list, driver, 'rain_start', 'Waiting for start signal...', '/opt/rain/rain.log')
        dlist.append(d)
    
    
    # Wait for all load drivers to start
    dl = defer.DeferredList(dlist)
    
    dl.addCallback(trigger_rain_benchmark, client_list)
    # dl.addCallback(finished, client_list)


def shutdown_glassfish_rain(client_list, ret=None):
    print "stopping glassfish and rain drivers..."
    logger.info('stopping glassfish and rain drivers')
    
    dlist = []
    
    for target in hosts.get_hosts('target'):
        print 'stopping glassfish on target %s' % (target) 
        d = base.launch(client_list, target, 'glassfish_stop')
        dlist.append(d)
    
    for target in hosts.get_hosts('load'):
        print 'stopping rain on target %s' % (target)
        d = base.launch(client_list, target, 'rain_stop')
        dlist.append(d)
    
    dl = defer.DeferredList(dlist)
    dl.addCallback(finished_end, client_list)
    

def phase_start_glassfish_database(done, client_list):
    """
    Rain has to be started after Glassfish is running! This is important because 
    the Rain Tracks of the SpecJ driver are accessing the Glassfish services. 
    """
    print 'starting glassfish and database...'
    logger.info('starting glassfish and database')
    
    try:
        dlist = []
        
        for target in hosts.get_hosts('target'):
            print '   * starting glassfish on target %s' % (target) 
            d = base.launch(client_list, target, 'glassfish_start', wait=False)
            dlist.append(d)
            
            d = base.poll_for_message(client_list, target, 'glassfish_wait', 'domain1 running')
            dlist.append(d)
        
        # Fill database in parallel
#        for target in hosts.get_hosts('database'):
#            print '   * initializing database on target %s' % (target)
#            d = base.launch(client_list, target, 'spec_dbload')
#            dlist.append(d)
        
        # Wait for all drones to finish and set phase
        dl = defer.DeferredList(dlist)
        
        # dl.addCallback(phase_start_rain, client_list)
        dl.addCallback(finished, client_list)
    except Exception, e:
        print e
        finished(None, client_list)
 
 
def phase_configure_glassfish(client_list):
    print 'reconfiguring glassfish ...'
    logger.info('reconfiguring glassfish')
    
    try:
        
        dlist = []
        
        for target in hosts.get_hosts('target'):
            print '   * configuring glassfish on target %s' % (target)
            
            mysql_name = target.replace('glassfish', 'mysql')
            print '     using mysql name: %s' % (mysql_name)
            drones.prepare_drone('glassfish_configure', 'domain.xml', mysql_server=mysql_name)
            drones.create_drone('glassfish_configure')
            
            d = base.launch(client_list, target, 'glassfish_configure', wait=True)
            dlist.append(d)
        
        # Wait for all drones to finish and set phase
        dl = defer.DeferredList(dlist)
        
        dl.addCallback(phase_start_glassfish_database, client_list)
        # dl.addCallback(finished, client_list)
        
    except Exception, e:
        print e
        finished(None, client_list)
 
 
def start_phase(client_list):
    logger.log(sonarlog.SYNC, 'start of startup sequence')
    
    print 'Connection established'
    print 'Following start sequence now...'
    phase_configure_glassfish(client_list)
    # phase_start_rain(None, client_list)
    # trigger_rain_benchmark(None, client_list)
    
    
def stop_phase(client_list):
    logger.log(sonarlog.SYNC, 'start of shutdown sequence')
    shutdown_glassfish_rain(client_list)
    
    
def errback(failure):
    print 'Error while executing'
    print failure
    reactor.stop()
    
def main():
    # Create drones
    drones.main()
    
    # Start or stop system
    start = True
    
    # Add hosts
    hosts.add_host('glassfish0', 'target')
#    hosts.add_host('glassfish1', 'target')
#    hosts.add_host('glassfish2', 'target')
#    hosts.add_host('glassfish3', 'target')
#    hosts.add_host('glassfish4', 'target')
#    hosts.add_host('glassfish5', 'target')
    hosts.add_host('mysql0', 'database')
#    hosts.add_host('mysql1', 'database')
#    hosts.add_host('mysql2', 'database')
#    hosts.add_host('mysql3', 'database')
#    hosts.add_host('mysql4', 'database')
#    hosts.add_host('mysql5', 'database')
#    hosts.add_host('load0', 'load')
#    hosts.add_host('load1', 'load')
    
    # Test rain start
    # phase_start_rain(None, None)
    # return
    
    # Connect with all drone relays
    hosts_map = hosts.get_hosts_list()
    dlist = base.connect(hosts_map)
        
    # Wait for all connections
    wait = defer.DeferredList(dlist)
    wait.addErrback(errback)
    
    # Decide what to do after connection setup
    if start:
        print 'starting system ...'
        wait.addCallback(start_phase)
    else:
        print 'stopping system ...'
        wait.addCallback(stop_phase)
    
    # Start the Twisted reactor
    reactor.run()

if __name__ == '__main__':
    sonarlog.connect()
    main()
    sonarlog.close()
