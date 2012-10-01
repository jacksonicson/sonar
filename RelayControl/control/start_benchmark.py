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
start = True
######################

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


def ram_up_finished(rain_clients, client_list):
    print 'end of startup sequence'
    logger.log(sonarlog.SYNC, 'end of startup sequence')
    finished(None, client_list)


def ramp_up(ret, rain_clients, client_list):
    print 'sleeping during ramp-up for %i seconds' % (ret)
    logger.info('sleeping during ramp-up for %i seconds' % (ret))
    reactor.callLater(ret, ram_up_finished, rain_clients, client_list)
    

def rain_started(ret, rain_clients, client_list):
    print 'rain is driving load now, waiting for ramp-up finish'
    logger.log(sonarlog.SYNC, 'start driving load')
    logger.info('querying ramp-up duration')
    
    d = rain_clients[0].getRampUpTime()
    d.addCallback(ramp_up, rain_clients, client_list) 

def rain_connection_failed(ret, client_list):
    print ret
    print 'Connection with Rain failed'
    print 'Known reasons: '
    print '   * Rain startup process took long which caused Twisted to time out'
    print '   * System was started the first time - Glassfish&SpecJ did not find the database initialized'
    print '   * Rain crashed - see rain.log on the load servers'
    reactor.callLater(10, trigger_rain_benchmark, None, client_list)

def rain_connected(rain_clients, client_list):
    print 'releasing load...'
    logger.info('releasing load on rain DRIVER_NODES')

    # Extract clients
    _rain_clients = []
    for client in rain_clients:
        _rain_clients.append(client[1].client)
        if client[0] == False:
            print 'Warn: Could not connect with all Rain servers'            
    rain_clients = _rain_clients
    
    # Release load
    dlist = []
    for client in rain_clients:
        print '   * releasing %s' % (client)
        logger.debug('releasing')
        
        d = client.startBenchmark(long(base.millis()))
        dlist.append(d)
    
    d = defer.DeferredList(dlist)
    d.addCallback(rain_started, rain_clients, client_list)
    

def trigger_rain_benchmark(ret, client_list):
    print 'connecting with rain DRIVER_NODES...'
    logger.info('connecting with rain DRIVER_NODES')
    
    dlist = []
    for driver in hosts.get_hosts('load'):
        print '   * connecting %s' % (driver)
        creator = ClientCreator(reactor,
                              TTwisted.ThriftClientProtocol,
                              RainService.Client,
                              TBinaryProtocol.TBinaryProtocolFactory(),
                              ).connectTCP(driver, 7852)
        dlist.append(creator)
        
    d = defer.DeferredList(dlist)                  
    d.addCallback(rain_connected, client_list)
    d.addErrback(rain_connection_failed, client_list)

def phase_start_rain(done, client_list):
    print 'starting rain DRIVER_NODES...'
    logger.info('starting rain DRIVER_NODES')
    
    # Dump profile
    profiles.dump(logger)
    
    dlist = []

    targets = hosts.get_hosts('target')
    target_count = len(targets)
    
    DRIVER_NODES = hosts.get_hosts('load')
    driver_count = len(DRIVER_NODES)
    
    targets_per_driver = int(math.ceil(float(target_count) / float(driver_count)))
    
    for i in range(0, driver_count):
        driver = DRIVER_NODES[i]
        
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
    
    
    # Wait for all load DRIVER_NODES to start
    dl = defer.DeferredList(dlist)
    
    dl.addCallback(trigger_rain_benchmark, client_list)
    # dl.addCallback(finished, client_list)


def shutdown_glassfish_rain(client_list, ret=None):
    print "stopping glassfish and rain DRIVER_NODES..."
    logger.info('stopping glassfish and rain DRIVER_NODES')
    
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
        if INIT_DB:
            for target in hosts.get_hosts('database'):
                print '   * initializing database on target %s' % (target)
                d = base.launch(client_list, target, 'spec_dbload')
                dlist.append(d)
        
        # Wait for all drones to finish and set phase
        dl = defer.DeferredList(dlist)
        
        dl.addCallback(phase_start_rain, client_list)
        # dl.addCallback(finished, client_list)
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
            
            # mysql_name = target.replace('glassfish', 'mysql')
            mysql_name = 'localhost'
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
    
    # Add host
    for i in xrange(0,18):
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
