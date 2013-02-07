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
* cmanager.py - configure the appropriate controller
* [controller].py - configure the controller 
* nodes.py - configure the infrastructure settings (node size, domain size, ..)
* domains.py - configure the number of domains
* profiles.py - select the workload mix
* driver.py - configure the workload simulation settings
'''

######################
# # CONFIGURATION    ##
######################
CONTROLLER = 'dsap'
SIM_ITERATIONS = 1
######################

# Setup logging
logger = sonarlog.getLogger('controller')

class MetricHandler(object):
    '''
    Receives metric data from the simulation or from Sonar
    and feeds the data into the model. The data is later used
    by the load balancer to resolve over- and underloads.
    '''
    def __init__(self, model):
        self.model = model
    
    def receive(self, datalist):
        for data in datalist:
            hostname = data.id.hostname
            
            host = self.model.get_host(hostname)
            if host == None:
                return
             
            host.put(data.reading)


class Controller(object):
    
    def __init__(self):
        self.scoreboard = scoreboard.Scoreboard()
        self.build_stragegy() 
    
    def model_initialize(self):
        self.model = model.Model
        
        # Flush model
        self.model.flush()
        
        # Run configuration
        if config.PRODUCTION: 
            self.model.model_from_current_allocation()
        else:
            migrations, _ = self.initial_placement()
            self.model.model_from_migrations(migrations)
        
        # Dump model
        self.model.dump()
        
        # Update empty counts
        active_server_info = self.model.server_active_info()
        print 'Updated active server count: %i' % active_server_info[0]
        logger.info('Active Servers: %s' % json.dumps({'count' : active_server_info[0],
                                                       'servers' : active_server_info[1],
                                                       'timestamp' : time.time()}))
    
        # Update scoreboard
        self.scoreboard.add_active_info(active_server_info[0], 0)
        
        #################################################
        # IMPORTANT #####################################
        #################################################
        # Initialize controller specific variables
        for host in self.model.get_hosts():
            host.blocked = 0


    def build_stragegy(self):
        # New message pump
        def heartbeat(pump):
            pump.callLater(10 * 60, heartbeat)
        self.pump = msgpump.Pump(heartbeat)
        
        if CONTROLLER == 'reactive': 
            import strategy_sandpiper_reactive
            self.strategy = strategy_sandpiper_reactive.Strategy(scoreboard, self.pump, model)
        elif CONTROLLER == 'proactive':
            import strategy_sandpiper_proactive
            self.strategy = strategy_sandpiper_proactive.Strategy(scoreboard, self.pump, model)
        elif CONTROLLER == 'round':
            import strategy_rr
            self.strategy = strategy_rr.Strategy(scoreboard, self.pump, model)
        elif CONTROLLER == 'file':
            import strategy_file
            self.strategy = strategy_file.Strategy(scoreboard, self.pump, model)
        elif CONTROLLER == 'sandpiper':
            from sandpiper import controller_sandpiper_standard  # @UnusedImport
            self.strategy = controller_sandpiper_standard.Strategy(scoreboard, self.pump, model)
        elif CONTROLLER == 'ssapv':
            import strategy_dsap
            import strategy_ssapv 
            self.strategy = strategy_ssapv.Strategy(scoreboard, self.pump, model)
        elif CONTROLLER == 'dsap':
            self.strategy = strategy_dsap.Strategy(scoreboard, self.pump, model)
        else:
            print 'No controller defined'
            return

    
    def start(self):
        # Build internal infrastructure representation
        self.model_initialize()
        
        # Create notification handler
        handler = MetricHandler(self.model)
        
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
            driver = driver.Driver(scoreboard, self.pump, model, handler)
            driver.start()
        
        # Start controller
        self.strategy.dump()
        self.strategy.start()
        
        # Start message pump
        self.pump.start()
        self.pump.join()


def launch_sim():
    name = '%s - %s' % (profiles.config.name, CONTROLLER)
    lines = []
    for _ in xrange(0, SIM_ITERATIONS):
        # Recreate domains
        domains.recreate()
        
        # Run controller
        controller = Controller()
        controller.start()
        
        # Get scoreboard statistics
        res = scoreboard.Scoreboard().get_result_line(controller.pump)
        scoreboard.Scoreboard().dump(controller.pump)
        lines.append(res)

    print 'Results: %s' % name        
    for line in lines:
        print line
          
            
if __name__ == '__main__':
    launch_sim() 
    

