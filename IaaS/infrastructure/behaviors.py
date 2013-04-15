from behaviorTree import behaviorTree as btree
from control import drones, hosts, base
from logs import sonarlog
from twisted.internet import defer, reactor

# Setup logging
logger = sonarlog.getLogger('start_benchmark')


class ConnectDomain(btree.Action):
    
    def __init__(self, hostname):
        self.hostname = hostname
    
    def action(self):
        # Rebuild all drones
        drones.build_all_drones()
        
        # Configure host
        hosts.clear()
        hosts.add_host(self.hostname, 'target')
        hosts.add_host(self.hostname, 'database')
        
        # Connect with all drone relays
        hosts_map = hosts.get_hosts_list()
        dlist = base.connect(hosts_map)
            
        # Wait for all connections
        wait = defer.DeferredList(dlist)
        d = defer.Deferred()
        wait.addCallback(self.start_phase, d)
        return d
        
    def start_phase(self, client_list, d):
        print 'connection established'
        print client_list
        self.blackboard.client_list = client_list
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



class StartGlassfishTree(object):
    
    def __init__(self, hostname):
        self.hostname = hostname
    
    def __inReactor(self):
        # Blackboard
        bb = btree.BlackBoard()
        
        # Start benchmark ###################################
        start = btree.Sequence(bb)
        start.add(ConnectDomain(self.hostname))
        start.add(ConfigureGlassfish())
        
        # Start Glassfish and database in parallel
        pl = btree.ParallelNode()
        start.add(pl)
        pl.add(StartGlassfish())
        pl.add(StartDatabase())
        
        # Launch behavior tree
        defer = start.execute()

    
    def launch(self):
        reactor.callFromThread(self.__inReactor)
