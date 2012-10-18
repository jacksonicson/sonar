from model import types
from threading import Thread
from logs import sonarlog
import driver
import model
import numpy as np
import time
import json

######################
## CONFIGURATION    ##
######################
PRODUCTION = True
START_WAIT = 60
INTERVAL = 30
THRESHOLD_OVERLOAD = 90
THRESHOLD_UNDERLOAD = 30
PERCENTILE = 75.0

K_VALUE = 20 # sliding windows size
M_VALUE = 15 # m values out of the window k must be above or below the threshold
######################

# Global migration ID counter
migration_id_counter = 0

# Setup logging
logger = sonarlog.getLogger('controller')

class LoadBalancer(Thread):
    '''
    Load balancer which design originated from Sandpiper
    '''
    
    def __init__(self, model):
        super(LoadBalancer, self).__init__()
        
        self.model = model
        self.running = True
    
    def stop(self):
        self.running = False
    
    def forecast(self, data):
        import statsmodels.api as sm
        import statsmodels as sm2

        model = sm2.tsa.ar_model.AR(data).fit()
        try:
            value = model.predict(len(data), len(data) + 1)
            return value[0]
        except:
            return data[-1]
        
        
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
            
            # Release block
            time_now = time.time()
            node_from.blocked = time_now
            node_to.blocked = time_now
            
            # Reset CPU consumption: Necessary because the old CPU readings
            # may trigger another migrations as they do not represent the load
            # without the VM
            node_from.flush(50)
            node_to.flush(50)
            
            print 'Migration finished'
            logger.info('Live Migration Finished: %s' % data)
        else:
            time_now = time.time()
            node_from.blocked = time_now
            node_to.blocked = time_now
            
            print 'Migration failed'
            logger.error('Live Migration Failed: %s' % data)
            
        # Log empty servers
        empty_count =  self.model.empty_count()
        print 'Updated empty count: %i' % empty_count
        logger.info('Server Empty: %s' % json.dumps({'count' : empty_count,
                                                     'timestamp' : time.time()}))
        
        
        
    def migrate(self, domain, source, target):
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
        
        data = json.dumps({'domain': domain.name, 'from': source.name, 'to': target.name, 'id': id})
        logger.info('Live Migration Triggered: %s' % data)
        
        # Backup current model status - for later analytics
        class info(object):
            pass
        info = info()
        info.migration_id = migration_id
        info.source_load_cpu = source.mean_load(K_VALUE)
        info.target_load_cpu = target.mean_load(K_VALUE)
        
        if PRODUCTION:
            from virtual import allocation
            allocation.migrateDomain(domain.name, source.name, target.name, self.callback, maxDowntime=10000, info=info)
        else:
            # TODO: Add some migration time simulation
            self.callback(domain.name, source.name, target.name, True, None)
        
    
    def run(self):
        # Gather data phase
        time.sleep(START_WAIT)
        logger.log(sonarlog.SYNC, 'Releasing load balancer')
        
        while self.running:
            # Sleeping till next balancing operation
            time.sleep(INTERVAL)
            print 'Running load balancer...'
            
            ############################################
            ## HOTSPOT DETECTOR ########################
            ############################################
            
            for node in model.get_hosts(types.NODE):
                # Check past readings
                readings = node.get_readings()
                
                # m out of the k last measurements are used to detect overloads 
                k = K_VALUE
                overload = 0
                underload = 0
                for reading in readings[-k:]:
                    if reading > THRESHOLD_OVERLOAD: overload += 1
                    if reading < THRESHOLD_UNDERLOAD: underload += 1

                m = M_VALUE
                overload = (overload >= m)
                underload = (underload >= m)
                 
                if overload:
                    print 'Overload in %s - %s' % (node.name, readings[-k:])  
                 
                # Update overload                                
                node.overloaded = overload
                node.underloaded = underload
                
                
            ############################################
            ## MIGRATION MANAGER #######################
            ############################################
            # Calculate volumes of each node
            nodes = []
            domains = []
            for node in model.get_hosts():
                volume = 1.0 / max(0.001, float(100.0 - node.percentile_load(PERCENTILE, k)) / 100.0)
                node.volume = volume
                node.volume_size = volume / 8.0 # 8 GByte
                
                if node.type == types.NODE:
                    nodes.append(node)
                elif node.type == types.DOMAIN: 
                    domains.append(node)
           
            # Sort nodes to their volume in DECREASING order
            # Multiplication with a big value to shift post comma digits to the front (integer)
            nodes.sort(lambda a, b: int((b.volume - a.volume) * 100000))
           
            
            ############################################
            ## MIGRATION TRIGGER #######################
            ############################################
            time_now = time.time()
            sleep_time = 10
            for node in nodes:
                node.dump()
                
                try:
                    # Overload situation
                    if node.overloaded:
                        # Source node to migrate from 
                        source = node
                        
                        # Sort domains by their VSR value in decreasing order 
                        node_domains = []
                        node_domains.extend(node.domains.values())
                        node_domains.sort(lambda a, b: int(b.volume_size - a.volume_size))
                        
                        # Try to migrate all domains by decreasing VSR value
                        for domain in node_domains:
                            
                            # Try all targets for the migration (reversed - starting at the BOTTOM)
                            for target in reversed(range(nodes.index(node) + 1, len(nodes))):
                                target = nodes[target]
                                
                                if len(target.domains) == 0:
                                    # print 'skip %s - %s' % (target.name, target.domains)
                                    continue
                                 
                                test = True
                                test &= (target.percentile_load(PERCENTILE, k) + (domain.percentile_load(PERCENTILE, k) / 2.0)) < THRESHOLD_OVERLOAD # Overload threshold
                                test &= len(target.domains) < 6
                                test &= (time_now - target.blocked) > sleep_time
                                test &= (time_now - source.blocked) > sleep_time
                                
                                if test: 
                                    print 'Overload migration: %s from %s to %s' % (domain.name, source.name, target.name)
                                    self.migrate(domain, source, target)
                                    raise StopIteration()
                                
                            for target in reversed(range(nodes.index(node) + 1, len(nodes))):
                                target = nodes[target]
                                 
                                test = True
                                test &= (target.percentile_load(PERCENTILE, k) + (domain.percentile_load(PERCENTILE, k) / 2.0)) < THRESHOLD_OVERLOAD # Overload threshold
                                test &= len(target.domains) < 6
                                test &= (time_now - target.blocked) > sleep_time
                                test &= (time_now - source.blocked) > sleep_time
                                
                                if test: 
                                    print 'Overload migration (Empty): %s from %s to %s' % (domain.name, source.name, target.name)
                                    self.migrate(domain, source, target)
                                    raise StopIteration()
                                
                except StopIteration: pass 
                
                try:
                    # Underload  situation
                    if node.underloaded:
                        # Source node to migrate from 
                        source = node
                        
                        # Sort domains by their VSR value in decreasing order 
                        node_domains = []
                        node_domains.extend(node.domains.values())
                        node_domains.sort(lambda a, b: int(b.volume_size - a.volume_size))
                        
                        # Try to migrate all domains by decreasing VSR value
                        for domain in node_domains:
                            
                            # Try all targets for the migration
                            for target in range(nodes.index(node) - 1):
                                target = nodes[target]
                                
                                if len(target.domains) == 0:
                                    continue
                                
                                test = True
                                test &= (target.percentile_load(PERCENTILE, k) + (domain.percentile_load(PERCENTILE, k) / 2.0)) < THRESHOLD_OVERLOAD # Overload threshold
                                test &= len(target.domains) < 6
                                test &= (time_now - target.blocked) > sleep_time
                                test &= (time_now - source.blocked) > sleep_time
                                
                                if test: 
                                    print 'Underload migration: %s from %s to %s' % (domain.name, source.name, target.name)
                                    self.migrate(domain, source, target)                                    
                                    raise StopIteration()
                            
                            
                            for target in range(nodes.index(node) - 1):
                                target = nodes[target]
                                
                                test = True
                                test &= (target.percentile_load(PERCENTILE, k) + (domain.percentile_load(PERCENTILE, k) / 2.0)) < THRESHOLD_OVERLOAD # Overload threshold
                                test &= len(target.domains) < 6
                                test &= (time_now - target.blocked) > sleep_time
                                test &= (time_now - source.blocked) > sleep_time
                                
                                if test: 
                                    print 'Underload migration (Empty): %s from %s to %s' % (domain.name, source.name, target.name)
                                    self.migrate(domain, source, target)                                    
                                    raise StopIteration()
                except StopIteration: pass
                

                
class MetricHandler:
    '''
    Receives metric data from the simulation or from Sonar
    and feeds the data into the model. The data is later used
    by the load balancer to resolve over- and underloads.
    '''
    def receive(self, datalist):
        # print 'handling...'
        for data in datalist:
            hostname = data.id.hostname
            
            host = model.get_host(hostname)
            if host == None:
                return
             
            host.put(data.reading)


def build_from_current_allocation():
    from virtual import allocation
    allocation = allocation.determine_current_allocation()
    
    for host in allocation.iterkeys():
        node = model.Node(host)
        
        for domain in allocation[host]:
            node.add_domain(model.Domain(domain))
    

def build_test_allocation():
    # Build internal infrastructure representation
    node = model.Node('srv0')
    node.add_domain(model.Domain('target0'))
    node.add_domain(model.Domain('target1'))
    
    node = model.Node('srv1')
    node.add_domain(model.Domain('target2'))
    node.add_domain(model.Domain('target3'))
    node.add_domain(model.Domain('target4'))
    node.add_domain(model.Domain('target5'))
    
    node = model.Node('srv2')
    node = model.Node('srv3')
    

def build_initial_model():
    if PRODUCTION: 
        # Build model from current allocation
        build_from_current_allocation()
    else:
        build_test_allocation()
    
    
    # Dump model
    model.dump()
    
    #################################################
    # IMPORTANT #####################################
    #################################################
    # Initialize controller specific variables
    for host in model.get_hosts():
        host.blocked = 0


def main():
    # Build internal infrastructure representation
    build_initial_model()

    # Create notification handler
    handler = MetricHandler()
    
    if PRODUCTION:
        # Connect with sonar to receive metric readings
        import connector
        connector.connect_sonar(model, handler)
    else:
        # Start the driver thread which simulates Sonar
        driver = driver.Driver(model, handler)
        driver.start()
    
    # Start load balancer thread which detects hotspots and triggers migrations
    balancer = LoadBalancer(model)
    balancer.start()
    
    # Wait for balancer to exit
    balancer.join()
    

if __name__ == '__main__':
    main()
    
