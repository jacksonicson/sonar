from logs import sonarlog
import controller
import json


######################
## CONFIGURATION    ##
######################
######################

# Setup logging
logger = sonarlog.getLogger('controller')

class DSAP(controller.LoadBalancer):
    
    def __init__(self, pump, model):
        super(DSAP, self).__init__(pump, model, 10*60)
        self.var = []
        
    def dump(self):
        print 'Dump DSAP controller configuration...'
        logger.info('Controller Configuration: %s' % json.dumps({'name' : 'Proactive',
                                                                 }))
    
    def balance(self):
        print 'Proactve (DSAP++ to come) - not controlling'
    
