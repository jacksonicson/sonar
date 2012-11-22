from logs import sonarlog
import configuration
import controller

######################
## CONFIGURATION    ##
######################
if configuration.PRODUCTION: 
    START_WAIT = 120
    INTERVAL = 20
    THRESHOLD_OVERLOAD = 90
    THRESHOLD_UNDERLOAD = 40
    PERCENTILE = 80.0
    THR_PERCENTILE = 0.2
else:
    START_WAIT = 0
    INTERVAL = 5
    THRESHOLD_OVERLOAD = 10
    THRESHOLD_UNDERLOAD = 10
    PERCENTILE = 80.0
    THR_PERCENTILE = 0.2


K_VALUE = 20 # sliding windows size
M_VALUE = 17 # m values out of the window k must be above or below the threshold
######################

# Setup logging
logger = sonarlog.getLogger('controller')



class Sandpiper(controller.LoadBalancer):
    
    def __init__(self, model, production):
        super(Sandpiper, self).__init__(model, production, INTERVAL)

    def lb(self):
        pass
        
    """def __init__(self, pump, model):
        super(Sandpiper, self).__init__(pump, model, INTERVAL)
        self.var = []"""        
        
    def post_migrate_hook(self, success, domain, node_from, node_to, end_time):
        pass
        
    def check_imbalance(self, time_now, sleep_time, k):   
        pass
        
    def check_hotspot(self, k):
        pass
        
    def migration_trigger(self, overload, nodes, node, k, sleep_time, time_now):
        pass    
        
    def balance(self):
        pass
        
        
# Test program
if __name__ == '__main__':
    print "DEBUG-Information"