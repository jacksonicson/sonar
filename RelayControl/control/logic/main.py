from control import domains
from logs import sonarlog
from workload import profiles
import configuration as config
import json
import model
import msgpump
import scoreboard
import time

'''
Conducting Simulations: 
* main() - configure the appropriate controller
* controller - configure the controller 
* nodes.py - configure the infrastructure settings (node size, domain size, ..)
* domains.py - configure the number of domains
* profiles.py - select the workload mix

Optional:
* driver.py - configure the workload simulation settings
'''

# Setup logging
logger = sonarlog.getLogger('controller')

class MetricHandler:
    '''
    Receives metric data from the simulation or from Sonar
    and feeds the data into the model. The data is later used
    by the load balancer to resolve over- and underloads.
    '''
    def receive(self, datalist):
        for data in datalist:
            hostname = data.id.hostname
            
            host = model.get_host(hostname)
            if host == None:
                return
             
            host.put(data.reading)
            


def build_from_current_allocation():
    from virtual import allocation
    allocation = allocation.determine_current_allocation()
    
    from virtual import nodes
    
    for host in allocation.iterkeys():
        node = model.Node(host, nodes.NODE_CPU_CORES)
        
        for domain in allocation[host]:
            node.add_domain(model.Domain(domain, nodes.DOMAIN_CPU_CORES))
    
def build_initial_model(controller):
    # Flush model
    model.flush()
    
    # Run configuration
    if config.PRODUCTION: 
        build_from_current_allocation()
    else:
        controller.initial_placement_sim()
    
    # Dump model
    model.dump()
    
    # Update empty counts
    active_server_info = model.server_active_info()
    print 'Updated active server count: %i' % active_server_info[0]
    logger.info('Active Servers: %s' % json.dumps({'count' : active_server_info[0],
                                                   'servers' : active_server_info[1],
                                                   'timestamp' : time.time()}))

    # Update scoreboard
    scoreboard.Scoreboard().add_active_info(active_server_info[0], 0)
    
    #################################################
    # IMPORTANT #####################################
    #################################################
    # Initialize controller specific variables
    for host in model.get_hosts():
        host.blocked = 0

def heartbeat(pump):
    print 'Message pump started'

def main(controller):
    # Flush scoreboard
    scoreboard.Scoreboard().flush()
    
    # New message pump
    pump = msgpump.Pump(heartbeat)
    
    # New controller
    import controller_ssapv #@UnusedImport
    import controller_sandpiper_reactive #@UnusedImport
    import controller_sandpiper_proactive #@UnusedImport
    import controller_rr #@UnusedImport
    import controller_file #@UnusedImport
    
    # ### CONTROLLER ##############################################
    if controller == 'reactive': 
        controller = controller_sandpiper_reactive.Sandpiper(pump, model)
    elif controller == 'proactive':
        controller = controller_sandpiper_proactive.Sandpiper(pump, model)
    elif controller == 'round':
        controller = controller_rr.Sandpiper(pump, model)
    elif controller =='file':
        controller = controller_file.Sandpiper(pump, model)
    else: 
        controller = controller_ssapv.Sandpiper(pump, model)
    # #############################################################
    
    # Build internal infrastructure representation
    build_initial_model(controller)
    
    # Create notification handler
    handler = MetricHandler()
    
    # Decides whether a simulation or a real
    # control system is run
    if config.PRODUCTION:
        # Connect with sonar to receive metric readings 
        # This will start a new service in a separate thread
        # The controller and simulation run single threaded by message pump
        import connector
        connector.connect_sonar(model, handler)
    else:
        # Start the driver thread which simulates Sonar
        import driver
        driver = driver.Driver(pump, model, handler)
        driver.start()
    
    # Start controller
    controller.dump()
    controller.start()
    
    # Start message pump
    pump.start()
    pump.join()
    return pump

if __name__ == '__main__':
    if config.PRODUCTION:
        # Controller is executed in production
        main()
    else:
        mix = profiles.config.name
        controller = 'reactive'
        postfix = 'experiment_360'
        
        name = '%s - %s - %s' % (mix, controller, postfix)
        t = open(config.path(name), 'w')
        for i in xrange(0, 15):
            domains.recreate()
            pump = main(controller)
            res = scoreboard.Scoreboard().get_result_line(pump)
            scoreboard.Scoreboard().dump(pump)
            t.write('%s\n' % res)
            t.flush()
        t.close()
    

