from logs import sonarlog
from virtual import nodes, placement
import controller
import json

######################
## CONFIGURATION    ##
######################
AGGREGATION = None
######################

# Setup logging
logger = sonarlog.getLogger('controller')

class Controller(controller.LoadBalancer):
    
    def __init__(self, scoreboard, pump, model):
        super(Controller, self).__init__(scoreboard, pump, model, 10 * 60, 120)
        self.var = []
        
    def dump(self):
        print 'Dump controller configuration...'
        logger.info('Controller Configuration: %s' % json.dumps({'name' : 'SSAPv',
                                                                 'aggregation' : AGGREGATION,
                                                                 }))
    # Initial placement calculation (simulation only!!!)
    def initial_placement_sim(self):
        nodecount = len(nodes.NODES)
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
    
