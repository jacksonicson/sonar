from logs import sonarlog
import controller
import json


######################
## CONFIGURATION    ##
######################
######################

# Setup logging
logger = sonarlog.getLogger('controller')

class Sandpiper(controller.LoadBalancer):
    
    def __init__(self, pump, model):
        super(Sandpiper, self).__init__(pump, model, 10*60)
        self.var = []
        
    def dump(self):
        print 'Dump Sandpiper controller configuration...'
        logger.info('Controller Configuration: %s' % json.dumps({'name' : 'Proactive',
                                                                 }))
    
    def balance(self):
        print 'Proactve (DSAP++ to come) - not controlling'
    
