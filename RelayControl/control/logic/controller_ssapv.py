from logs import sonarlog
from virtual import nodes
import controller
import json
import placement

######################
## CONFIGURATION    ##
######################
AGGREGATION = None
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
                                                                 'aggregation' : AGGREGATION,
                                                                 }))
    # Initial placement calculation (simulation only!!!)
    def initial_placement_sim(self):
        nodecount = len(nodes.HOSTS)
        splace = placement.SSAPvPlacement(nodecount, nodes.NODE_CPU, nodes.NODE_MEM, nodes.DOMAIN_MEM)
        
        if AGGREGATION == None:
            migrations, _ = splace.execute(aggregation=False)
        else:
            migrations, _ = splace.execute(aggregation=True, bucketCount=AGGREGATION)
            
        self.build_internal_model(migrations)
        return migrations
    
    def balance(self):
        # print 'SSAPv static - not controlling'
        pass
    
