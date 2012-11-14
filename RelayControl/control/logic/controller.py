'''
Base class for controllers
'''

from logs import sonarlog
from threading import Thread
import json
import scoreboard
import threading
import time
import util

######################
## CONFIGURATION    ##
######################
START_WAIT = 0
######################

# Global migration ID counter (identifies migrations)
migration_id_counter = 0

# Setup Sonar logging
logger = sonarlog.getLogger('controller')

class LoadBalancer(Thread):
    '''
    Base class of a load balancer
    '''
    
    def __init__(self, model, production, interval):
        super(LoadBalancer, self).__init__()
        
        # Data model
        self.model = model
        
        # Production mode 
        self.production = production
        
        # Execution interval
        self.interval = util.adjust_for_speedup(interval)
        
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
            
            # Call post migration hook in concrete controller implementation
            self.post_migrate_hook(True, domain, node_from, node_to)
            
            print 'Migration finished'
            logger.info('Live Migration Finished: %s' % data)
            
        else:
            # Call post migration hook in concrete controller implementation
            self.post_migrate_hook(False, domain, node_from, node_to)
            
            print 'Migration failed'
            logger.error('Live Migration Failed: %s' % data)
            
        # Log number of empty servers
        active_server_info = self.model.server_active_info()
        print 'Updated active server count: %i' % active_server_info[0]
        logger.info('Active Servers: %s' % json.dumps({'count' : active_server_info[0],
                                                       'servers' : active_server_info[1],
                                                       'timestamp' : util.time()}))
        
        # Update internal scoreboard
        sb = scoreboard.Scoreboard()
        sb.add_active_info(active_server_info[0])
        
        
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
        now_time = util.time()
        source.blocked = now_time + util.adjust_for_speedup(60 * 60)
        target.blocked = now_time + util.adjust_for_speedup(60 * 60)
        
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
            # Call migration code and hand over the callback reference
            from virtual import allocation
            allocation.migrateDomain(domain.name, source.name, target.name, self.callback, maxDowntime=10000, info=info)
        else:
            # TODO: Run some migration simulation
            self.callback(domain.name, source.name, target.name, 0, 0, info, True, None)
        
        
    def lb(self):
        print 'No load balancer implemented'
        pass
    
    def dump(self):
        pass
    
    def domain_to_server_cpu(self, target, domain, domain_cpu):
        domain_cpu_factor = target.cpu_cores / domain.cpu_cores
        return domain_cpu / domain_cpu_factor
    
    def run(self):
        # Gather data phase
        time.sleep(START_WAIT)
        logger.log(sonarlog.SYNC, 'Releasing load balancer')
        
        while self.running:
            # Wait for next control cycle
            print 'Wait for next control cycle...'
            self.event.wait(self.interval)
            if self.running == False:
                break
            
            print 'Running load balancer...'
            self.lb()
            
            if not self.production:
                print 'Scoreboard:'      
                sb = scoreboard.Scoreboard()
                sb.dump() 
                
