from analytics import forecasting as smoother
from logs import sonarlog
from model import types
from workload import profiles
import configuration
import controller
import json
import numpy as np

######################
## CONFIGURATION    ##
######################
######################

# Setup logging
logger = sonarlog.getLogger('controller')

class Sandpiper(controller.LoadBalancer):
    
    def __init__(self, pump, model):
        super(Sandpiper, self).__init__(pump, model, 10 * 60, 120)
        self.var = []
        
    def dump(self):
        print 'Dump Sandpiper controller configuration...'
        logger.info('Controller Configuration: %s' % json.dumps({'name' : 'SSAPv',
                                                                 }))
    
    def initial_placement_sim(self):
        import placement
        from virtual import nodes
        from control import domains 
        
        nodecount = len(nodes.HOSTS)
        splace = placement.SSAPvPlacement(nodecount, nodes.NODE_CPU, nodes.NODE_MEM, nodes.DOMAIN_MEM)
        migrations, _ = splace.execute(aggregation=False , bucketCount=12)
        self.build_internal_model(migrations)
        return migrations 
    
    
    def balance(self):
        print 'SSAPv static - not controlling'
    
