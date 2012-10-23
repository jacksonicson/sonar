from threading import Thread
from logs import sonarlog
import time
import json
import threading

######################
## CONFIGURATION    ##
######################
START_WAIT = 0
######################

# Global migration ID counter
migration_id_counter = 0

# Setup logging
logger = sonarlog.getLogger('controller')

class LoadBalancer(Thread):
    '''
    Base class of a load balancer
    '''
    
    def __init__(self, model, production, interval):
        super(LoadBalancer, self).__init__()
        
        self.model = model
        self.production = production
        self.interval = interval
        
        self.running = True
        self.event = threading.Event()
    
    
    def stop(self):
        self.running = False
        self.event.set()
    
    
    def post_migrate_hook(self):
        pass
    
    def callback(self, domain, node_from, node_to, start, end, info, status, error):
        node_from = self.model.get_host(node_from)
        node_to = self.model.get_host(node_to)
        domain = self.model.get_host(domain)
        duration = end - start
        
        data = json.dumps({'domain': domain.name, 'from': node_from.name,
                           'to': node_to.name, 'start' : start, 'end' : end,
                           'duration' : duration, 
                           'id': info.migration_id,
                           'source_cpu' : info.source_load_cpu,
                           'target_cpu' : info.target_load_cpu})
        
        # Check if migration was successful
        if status == True: 
            node_to.domains[domain.name] = domain
            del node_from.domains[domain.name]
            
            self.post_migrate_hook(True, domain, node_from, node_to)
            
            print 'Migration finished'
            logger.info('Live Migration Finished: %s' % data)
            
        else:
            
            print 'Migration failed'
            self.post_migrate_hook(False, domain, node_from, node_to)
            logger.error('Live Migration Failed: %s' % data)
            
        # Log empty servers
        active_server_info =  self.model.server_active_info()
        print 'Updated active server count: %i' % active_server_info[0]
        logger.info('Active Servers: %s' % json.dumps({'count' : active_server_info[0],
                                                       'servers: ' : active_server_info[1],
                                                       'timestamp' : time.time()}))
        
        
        
    def migrate(self, domain, source, target, kvalue):
        print 'Migration triggered'
        assert(source != target)
        
        # Update counter
        global migration_id_counter
        migration_id = migration_id_counter
        migration_id_counter += 1
        
        # Block source and target nodes
        # Set block times in the future to guarantee that the block does not run out 
        # until the migration is finished
        now_time = time.time()
        source.blocked = now_time + 60 * 60
        target.blocked = now_time + 60 * 60
        
        data = json.dumps({'domain': domain.name, 'from': source.name, 'to': target.name, 'id': migration_id})
        logger.info('Live Migration Triggered: %s' % data)
        
        # Backup current model status - for later analytics
        class info(object):
            pass
        
        info = info()
        info.migration_id = migration_id
        info.source_load_cpu = source.mean_load(kvalue)
        info.target_load_cpu = target.mean_load(kvalue)
        
        if self.production:
            from virtual import allocation
            allocation.migrateDomain(domain.name, source.name, target.name, self.callback, maxDowntime=10000, info=info)
        else:
            # TODO: Add some migration time simulation
            self.callback(domain.name, source.name, target.name, True, None)
        
        
    def lb(self):
        print 'No load balancer implemented'
        pass
    
    def dump(self):
        pass
    
    def run(self):
        # Gather data phase
        time.sleep(START_WAIT)
        logger.log(sonarlog.SYNC, 'Releasing load balancer')
        
        while self.running:
            # Sleeping till next balancing operation
            # time.sleep(INTERVAL)
            self.event.wait(self.interval)
            if self.running == False:
                break
            
            print 'Running load balancer...'
            self.lb()
                
