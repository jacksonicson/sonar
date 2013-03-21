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
* controller.py - configure the appropriate strategy
* [controller].py - configure the strategy 
* nodes.py - configure the infrastructure settings (node size, domain size, ..)
* domains.py - configure the number of domains
* profiles.py - select the workload mix
* driver.py - configure the workload simulation settings
'''

'''
Strategies:
- reactive
- proactive
- round
- file
- sandpiper
- ssapv
- dsap
'''

######################
# # CONFIGURATION    ##
######################
STRATEGY = 'sandpiper' 
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
        # Create  new model
        self.model = model.Model()

        # Setup the strategy        
        self.build_stragegy()
         
    def model_initialize(self):
        # Run configuration
        if config.PRODUCTION: 
            # Load current infrastructure state into model
            self.model.model_from_current_allocation()
        else:
            # Load calculated initial placement into model
            migrations, _ = self.strategy.initial_placement()
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
            pump.callLater(10 * 60, heartbeat, pump)
        self.pump = msgpump.Pump(heartbeat)
        
        # Create scoreboard
        self.scoreboard = scoreboard.Scoreboard(self.pump)
        
        # Create controller based on the strategy
        if STRATEGY == 'reactive': 
            import strategy_sandpiper_reactive
            self.strategy = strategy_sandpiper_reactive.Strategy(self.scoreboard, self.pump, self.model)
        elif STRATEGY == 'proactive':
            import strategy_sandpiper_proactive
            self.strategy = strategy_sandpiper_proactive.Strategy(self.scoreboard, self.pump, self.model)
        elif STRATEGY == 'round':
            import strategy_rr
            self.strategy = strategy_rr.Strategy(self.scoreboard, self.pump, self.model)
        elif STRATEGY == 'file':
            import strategy_file
            self.strategy = strategy_file.Strategy(self.scoreboard, self.pump, self.model)
        elif STRATEGY == 'sandpiper':
            from sandpiper import strategy_sandpiper_standard  # @UnusedImport
            self.strategy = strategy_sandpiper_standard.Strategy(self.scoreboard, self.pump, self.model)
        elif STRATEGY == 'ssapv':
            import strategy_ssapv 
            self.strategy = strategy_ssapv.Strategy(self.scoreboard, self.pump, self.model)
        elif STRATEGY == 'dsap':
            import strategy_dsap
            self.strategy = strategy_dsap.Strategy(self.scoreboard, self.pump, self.model)
        else:
            print 'No controller defined'
            return

    
    def start(self):
        # Build model - This has to be executed at start not in init
        # The setup routine creates a Controller instance and then
        # calculates and establishes the initial placement. If the 
        # model was initialized in the init method it would aquire the
        # infrastructure state before the calculated initial placement
        # was established  
        self.model_initialize()
        
        # Create notification handler
        self.handler = MetricHandler(self.model)
        
        # Decides whether a simulation or a real
        # control system is run
        if config.PRODUCTION:
            # Connect with sonar to receive metric readings 
            # This will start a new service in a separate thread
            # The controller and simulation run single threaded by message pump
            import connector
            connector.connect_sonar(self.model, self.handler)
        else:
            # Use the workload driver to simulate Sonar
            import driver
            driver = driver.Driver(self.scoreboard, self.pump, self.model, self.handler)
            driver.start()
        
        # Start controller
        self.strategy.dump()
        self.strategy.start()
        
        # Start message pump
        self.pump.start()
        self.pump.join()


def launch_sim():
    name = '%s - %s' % (profiles.config.name, STRATEGY)
    lines = []
    for _ in xrange(0, SIM_ITERATIONS):
        # Recreate domains
        domains.recreate()
        
        # Run controller
        controller = Controller()
        controller.start()
        
        # Get scoreboard statistics
        res = controller.scoreboard.get_result_line()
        controller.scoreboard.dump()
        lines.append(res)

    print 'Results: %s' % name        
    for line in lines:
        print line
          
            
if __name__ == '__main__':
    launch_sim() 
    

