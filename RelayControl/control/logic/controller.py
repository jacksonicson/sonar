import model
import threading
import sandpiper
import configuration as config
import json
from logs import sonarlog
import time

# Setup logging
logger = sonarlog.getLogger('controller')

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
    if config.PRODUCTION: 
        # Build model from current allocation
        build_from_current_allocation()
    else:
        build_test_allocation()
    
    # Dump model
    model.dump()
    
    # Update empty counts
    empty_count =  model.empty_count()
    print 'Updated empty count: %i' % empty_count
    logger.info('Server Empty: %s' % json.dumps({'count' : empty_count,
                                                     'timestamp' : time.time()}))
    
    #################################################
    # IMPORTANT #####################################
    #################################################
    # Initialize controller specific variables
    for host in model.get_hosts():
        host.blocked = 0


# Globals
driver = None
balancer = None
exited = False
condition = threading.Condition()

# React to kill signals
def sigtermHandler(signum, frame):
    condition.acquire()
    
    global exited
    exited = True
    condition.notify()
    
    condition.release()


def dump():
    balancer.dump()


def main():
    global driver
    global balancer
    
    # Build internal infrastructure representation
    build_initial_model()

    # Create notification handler
    handler = MetricHandler()
    
    if config.PRODUCTION:
        # Connect with sonar to receive metric readings
        import connector
        connector.connect_sonar(model, handler)
    else:
        # Start the driver thread which simulates Sonar
        import driver
        driver = driver.Driver(model, handler)
        driver.start()
    
    # Start load balancer thread which detects hot-spots and triggers migrations
    balancer = sandpiper.Sandpiper(model, config.PRODUCTION)
    balancer.start()
    
    # Dump configuration
    dump()

    # Register the signal handlers
    import signal
    signal.signal(signal.SIGTERM, sigtermHandler)
    
    # Wait for balancer to exit
    print 'Controller is functional...'
    
    
    print 'Waiting for shutdown event...'
    
    # acquire condition
    condition.acquire()

    # Spinning until shutdown signal is received
    global exited        
    while exited == False:
        try:
            condition.wait(10)
        except KeyboardInterrupt:
            exited = True
            continue

    # releasing condition
    condition.release()
    
    # Shutdown
    print 'Shutting down now... ',
    if driver is not None:
        driver.stop()
        
    if balancer is not None:
        balancer.stop()
    
    print 'Waiting for threads to finish...'
    
    

if __name__ == '__main__':
    main()
    
