from twisted.internet import defer, reactor
from behaviorTree import behaviorTree

######################
## CONFIGURATION    ##
######################
INIT_DB = True
start = False
######################

# creating drones
class ConnectionSetup(behaviorTree.Action):
    def action(self):
        d = defer.Deferred()
        print 'Connection Setup...'
        # Create drones
        drones.main()
        
        # Setup initial allocation
        if start:
            initial_allocation()
        
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
        wait.addErrback(self.errback, d)
        wait.addCallback(self.start_phase, d)
      
        return d
     
    def start_phase(self, client_list, d)
        self.blackboard.addData("client_list", client_list)
        reactor.callLater(0, d.callback, True)
    
    def errback(self, d):
        reactor.callLater(0, d.callback, False)
    
class ConfigureGlassfish(behaviorTree.Action):
    def action(self):
        actionDef = defer.Deferred()
        client_list = self.blackboard.getData("client_list")
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
            dl.addCallback(self.phase_config_glassfish_done, actionDef)
            
        except Exception, e:
            print e
            reactor.callLater(0, actionDef.callback, False)
        
        return actionDef
    
    def phase_config_glassfish_done(self, actionDef):
        reactor.callLater(0, actionDef.callback, True)

class StartGlassfish(behaviorTree.Action):
    def action(self):
        actionDef = defer.Deferred()
        client_list = self.blackboard.getData("client_list")
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
            
            # Wait for all drones to finish and set phase
            dl = defer.DeferredList(dlist)
            dl.addCallback(self.phase_start_glassfish_done, actionDef)
            
        except Exception, e:
            print e
            reactor.callLater(0, actionDef.callback, False)
        
        return actionDef
    
    def phase_start_glassfish_done(self, actionDef):
        reactor.callLater(0, actionDef.callback, True)
        
class StartDatabase(behaviorTree.Action):
    def action(self):
        actionDef = defer.Deferred()
        client_list = self.blackboard.getData("client_list")
        print 'Initialize the Database...'
        logger.info('Initializing the database')
        
        try:
            dlist = []
            # Fill database 
            if INIT_DB:
                for target in hosts.get_hosts('database'):
                    print '   * initializing database on target %s' % (target)
                    d = base.launch(client_list, target, 'spec_dbload')
                    dlist.append(d)
            
            # Wait for all drones to finish and set phase
            dl = defer.DeferredList(dlist)
            
            dl.addCallback(self.phase_start_database_done, actionDef)
           
        except Exception, e:
            print e
            reactor.callLater(0, actionDef.callback, False)
        
        return actionDef
    
    def phase_start_database_done(self, actionDef):
        reactor.callLater(0, actionDef.callback, True)

class StartRain(behaviorTree.Action):
    def action(self):
        actionDef = defer.Deferred()
        client_list = self.blackboard.getData("client_list")
       
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
        
        dl.addCallback(self.phase_start_rain_done, actionDef)
        return actionDef
        
    def phase_start_rain_done(self, actionDef):
        reactor.callLater(1, actionDef.callback, True)
        
class TriggerRainBenchmark(behaviorTree.Action):
    def action(self):
        actionDef = defer.Deferred()
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
            
        d = defer.DeferredList(dlist)                  
        d.addCallback(self.trigger_rain_benchmark_done, actionDef)
        d.addErrback(self.errback, actionDef)
        return actionDef
    
    def trigger_rain_benchmark_done(self, rain_clients, actionDef):
        self.blackboard.addData("rain_clients", rain_clients)
        reactor.callLater(0, actionDef.callback, True)
    
    def errback(self, actionDef):
        reactor.callLater(0, actionDef.callback, False)

class ReleaseLoad(behaviorTree.Action):
    def action(self):
        actionDef = defer.Deferred()
        rain_clients = self.blackboard.getData("rain_clients")
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
        d.addCallback(self.loadReleased, actionDef)
        
        return actionDef
    
    def loadReleased(self, actionDef):
        reactor.callLater(0, actionDef.callback, True)

class SleepDuringRampup(behaviorTree.Action):
    def action(self):
        actionDef = defer.Deferred()
        rain_clients = self.blackboard.getData("rain_clients")
        print 'rain is driving load now, waiting for ramp-up finish'
        logger.log(sonarlog.SYNC, 'start driving load')
        logger.info('querying ramp-up duration')
        
        d = rain_clients[0].getRampUpTime()
        d.addCallback(self.rain_start_done, actionDef) 
        return actionDef
        
    def rain_start_done(self, ret, actionDef):
        self.blackboard.addData("ret", ret)
        print 'sleeping during ramp-up for %i seconds' % (ret)
        logger.info('sleeping during ramp-up for %i seconds' % (ret))
        reactor.callLater(ret, actionDef.callback, True)

def finished(data):    
    print 'finish phase'
    logger.log(sonarlog.SYNC, 'end of startup sequence')
    
    if reactor.running:
        reactor.stop()

    # Launch the controller
    print '### CONTROLLER ###############################'
    print 'starting controller'
    logger.info('loading controller')
    
    from control.logic import controller
    controller.main()

def main():
    b = behaviorTree.BlackBoard()
    parallelTasks = behaviorTree.ParallelNode(b).addChild(StartGlassfish(b)).addChild(StartDatabase(b))
    mainSequence = behaviorTree.Sequence(b).addChild(ConnectionSetup(b)).addChild(ConfigureGlassfish(b)).addChild(parallelTasks).addChild(StartRain(b)).addChild(TriggerRainBenchmark(b)).addChild(ReleaseLoad(b)).addChild(SleepDuringRampup(b))
    d = mainSequence.execute()     
    d.addCallback(finished)
    
    # Start the Twisted reactor
    reactor.run()

if __name__ == '__main__':
    sonarlog.connect()
    main()
    
