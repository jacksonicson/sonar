from logs import sonarlog
import logic

######################
## CONFIGURATION    ##
######################
START_WAIT = 0
INTERVAL = 5                    #20
THRESHOLD_OVERLOAD = 10         #90
THRESHOLD_UNDERLOAD = 10        #40
PERCENTILE = 80.0

K_VALUE = 20 # sliding windows size
M_VALUE = 17 # m values out of the window k must be above or below the threshold
######################

# Setup logging
logger = sonarlog.getLogger('controller')

class Sandpiper(logic.LoadBalancer):
    
    def __init__(self, model, production):
        super(Sandpiper, self).__init__(model, production, INTERVAL)

    def lb(self):
        pass
        print "lb-methode"
        
# Test program
if __name__ == '__main__':
    print "DEBUG-Information"