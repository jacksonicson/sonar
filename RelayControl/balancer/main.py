from control import domains
from logs import sonarlog
from workload import profiles
import configuration as config
import json
import model
import msgpump
import scoreboard
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
    

def build_test_allocation():
    import placement
    from virtual import nodes
    from control import domains 
    
    nodecount = len(nodes.HOSTS)
    splace = placement.FirstFitPlacement(nodecount, nodes.NODE_CPU, nodes.NODE_MEM, nodes.DOMAIN_MEM)
    migrations, _ = splace.execute()
    
    _nodes = []
    for node in nodes.NODES: 
        mnode = model.Node(node, nodes.NODE_CPU_CORES)
        _nodes.append(mnode)
        
    _domains = {}
    for domain in domains.domain_profile_mapping:
        dom = model.Domain(domain.domain, nodes.DOMAIN_CPU_CORES)
        _domains[domain.domain] = dom
        
    for migration in migrations:
        print migration 
        _nodes[migration[1]].add_domain(_domains[migration[0]]) 
    
 
def build_debug_allocation():    
    # Build internal infrastructure representation
    node = model.Node('srv0', 4)
    node.add_domain(model.Domain('target0', 2))
    node.add_domain(model.Domain('target1', 2))
    
    node = model.Node('srv1', 4)
    node.add_domain(model.Domain('target2', 2))
    node.add_domain(model.Domain('target3', 2))
    node.add_domain(model.Domain('target4', 2))
    node.add_domain(model.Domain('target5', 2))
    
    node = model.Node('srv2', 4)
    node = model.Node('srv3', 4)
    

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
    from sandpiper_advanced import sandpiper_standard #@UnusedImport
    
    # ### CONTROLLER ##############################################
    if controller == 'reactive': 
        controller = controller_sandpiper_reactive.Sandpiper(pump, model)
    elif controller == 'proactive':
        controller = controller_sandpiper_proactive.Sandpiper(pump, model)
    elif controller == 'round':
        controller = controller_rr.Sandpiper(pump, model)
    elif controller == 'johannes':
        controller = sandpiper_standard.Sandpiper(pump, model)
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
        controller = 'johannes'
        ctype = 'experiment'
        name = 'test'
        t = open(config.path(name), 'w')
        for i in xrange(0, 30):
            domains.mapping()
            pump = main(controller)
            res = scoreboard.Scoreboard().get_result_line(pump)
            scoreboard.Scoreboard().dump(pump)
            t.write('%s\n' % res)
            t.flush()
        t.close()
    

