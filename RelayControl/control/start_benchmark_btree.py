from balancer import controller
from behaviorTree import behaviorTree as btree
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

# Strategy instance
controller = controller.Strategy()

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
        d = defer.Deferred()
        wait.addCallback(self.start_phase, d)
        return d
        
    def start_phase(self, client_list, d):
        print 'Start phase ended'
        self.blackboard.client_list = client_list
        d.callback(True)


class StopGlassfishRain(btree.Action):
    def action(self):
        print "stopping glassfish and rain DRIVER_NODES..."
        logger.info('stopping glassfish and rain DRIVER_NODES')
        
        dlist = []
        
        for target in hosts.get_hosts('target'):
            print 'stopping glassfish on target %s' % (target) 
            d = base.launch(self.blackboard.client_list, target, 'glassfish_stop')
            dlist.append(d)
        
        for target in hosts.get_hosts('load'):
            print 'stopping rain on target %s' % (target)
            d = base.launch(self.blackboard.client_list, target, 'rain_stop')
            dlist.append(d)
        
        dl = defer.DeferredList(dlist)
        d = defer.Deferred()
        dl.addCallback(self.ok, d)
        return d
        
    def ok(self, status, d):
        d.callback(True)
    
   
class startController(btree.Action):
    def action(self):
        print '### CONTROLLER ###############################'
        controller.start()
        return defer.Deferred()
    
   
class TriggerRain(btree.Action):
    def action(self):
        print 'releasing load...'
        logger.info('releasing load on rain DRIVER_NODES')
    
        # Extract clients
        _rain_clients = []
        for client in self.blackboard.rain_clients:
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

        self.d = defer.Deferred()
        dl = defer.DeferredList(dlist)
        dl.addCallback(self.rain_started)
        return self.d
        
    def rain_started(self, status):
        print 'rain is driving load now, waiting for ramp-up finish'
        logger.log(sonarlog.SYNC, 'start driving load')
        logger.info('querying ramp-up duration')
        
        d = self.blackboard.rain_clients[0].getRampUpTime()
        d.addCallback(self.ramp_up)
        
    def ramp_up(self, ret):
        print 'sleeping during ramp-up for %i seconds' % (ret)
        logger.info('sleeping during ramp-up for %i seconds' % (ret))
        reactor.callLater(ret, self.ram_up_finished)
        
    def ram_up_finished(self):
        print 'end of startup sequence'
        logger.log(sonarlog.SYNC, 'end of startup sequence')
        self.d.callback(True)
        
    
class ConnectRain(btree.Action):
    def action(self, d=None):
        print 'connecting with rain DRIVER_NODES...'
        logger.info('connecting with rain DRIVER_NODES')
        
        dlist = []
        for driver in hosts.get_hosts('load'):
            print '   * connecting %s' % (driver)
            creator = ClientCreator(reactor,
                                  TTwisted.ThriftClientProtocol,
                                  RainService.Client,
                                  TBinaryProtocol.TBinaryProtocolFactory(),
                                  ).connectTCP(driver, 7852, timeout=120)
            dlist.append(creator)
          
        if d == None:
            d = defer.Deferred()  
        dl = defer.DeferredList(dlist)                  
        dl.addCallback(self.ok, d)
        dl.addErrback(self.err, d)
        return d
        
    def ok(self, status, d):
        self.blackboard.rain_clients = status
        print 'Clients'
        print status
        d.callback(True)
        
    def err(self, status, d):
        print 'Connection with Rain failed'
        print 'Known reasons: '
        print '   * Rain startup process took long which caused Twisted to time out'
        print '   * System was started the first time - Glassfish&SpecJ did not find the database initialized'
        print '   * Rain crashed - see rain.log on the load servers'
        reactor.callLater(10, self.action, d)
    
class StartRain(btree.Action):
    
    def action(self):
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
                
                # Important: Load the USER workload profile
                config_target['profile'] = domains.user_profile_by_name(target)
                config_targets.append(config_target)
    
            print config_targets
    
            # Configure drone
            drones.prepare_drone('rain_start', 'rain.config.specj.json', targets=config_targets)
            drones.create_drone('rain_start')
            
            # Launch this drone
            d = base.wait_for_message(self.blackboard.client_list, driver, 'rain_start', 'Waiting for start signal...', '/opt/rain/rain.log')
            dlist.append(d)
        
        
        # Wait for all load DRIVER_NODES to start
        d = defer.Deferred()
        dl = defer.DeferredList(dlist)
        dl.addCallback(self.ok, d)
        return d
        
    def ok(self, status, d):
        d.callback(True)
            

class StartDatabase(btree.Action):
    def action(self):
        print 'starting database...'
        logger.info('starting database')
        
        try:
            dlist = []
            for target in hosts.get_hosts('database'):
                print '   * initializing database on target %s' % (target)
                d = base.launch(self.blackboard.client_list, target, 'spec_dbload')
                dlist.append(d)
            
            # Wait for all drones to finish and set phase
            d = defer.Deferred()
            dl = defer.DeferredList(dlist)
            dl.addCallback(self.ok, d)
            return d
            
        except Exception, e:
            print e
            return False
        
    def ok(self, status, d):
        d.callback(True)
        

class StartGlassfish(btree.Action):
    def action(self):
        print 'starting glassfish...'
        logger.info('starting glassfish')
        
        try:
            dlist = []
            
            for target in hosts.get_hosts('target'):
                print '   * starting glassfish on target %s' % (target) 
                d = base.launch(self.blackboard.client_list, target, 'glassfish_start', wait=False)
                dlist.append(d)
                
                d = base.poll_for_message(self.blackboard.client_list, target, 'glassfish_wait', 'domain1 running')
                dlist.append(d)
            
            # Wait for all drones to finish and set phase
            d = defer.Deferred()
            dl = defer.DeferredList(dlist)
            dl.addCallback(self.ok, d)
            return d
            
        except Exception, e:
            print e
            return False
        
    def ok(self, status, d):
        d.callback(True)
        

class ConfigureGlassfish(btree.Action):
    def action(self):
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
                
                d = base.launch(self.blackboard.client_list, target, 'glassfish_configure', wait=True)
                dlist.append(d)
            
            # Wait for all drones to finish and set phase
            dl = defer.DeferredList(dlist)
            d = defer.Deferred()
            dl.addCallback(self.ok, d)
            return d
            
        except Exception, e:
            print e
            return False
            
    def ok(self, status, d):
        d.callback(True)


def errback(failure):
    print 'Error while executing'
    print failure

def finished(data):
    print 'Behavior reached end'
    if reactor.running:
        reactor.stop()

def main():
    # Blackboard
    bb = btree.BlackBoard()
    
    # Start benchmark
    start = btree.Sequence(bb)
    start.add(AllocateDomains())
#    start.add(ConfigureGlassfish())
#    
#    pl = btree.ParallelNode()
#    start.add(pl)
#    pl.add(StartGlassfish())
#    pl.add(StartDatabase())
#    
#    start.add(StartRain())
#    start.add(ConnectRain())
#    start.add(TriggerRain())
    start.add(startController())
    
    # Stop benchmark
    stop = btree.Sequence(bb)
    stop.add(AllocateDomains())
    stop.add(StopGlassfishRain())
    
    # Execute behavior trees
    defer = start.execute()     
    defer.addCallback(finished)
    
    # Start the Twisted reactor
    reactor.run()

if __name__ == '__main__':
    sonarlog.connect()
    main()
    
