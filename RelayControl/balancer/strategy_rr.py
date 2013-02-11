from logs import sonarlog
import strategy
import json

######################
# # CONFIGURATION    ##
######################
######################

# Setup logging
logger = sonarlog.getLogger('controller')

class Strategy(strategy.StrategyBase):
    
    def __init__(self, scoreboard, pump, model):
        super(Strategy, self).__init__(scoreboard, pump, model, 10 * 60, 120)
        self.var = []
        
    def dump(self):
        print 'Dump Sandpiper controller configuration...'
        logger.info('Strategy Configuration: %s' % json.dumps({'name' : 'SSAPv',
                                                                 }))
    
    def initial_placement(self):
        from virtual import placement
        from virtual import nodes
        
        nodecount = len(nodes.NODES)
        splace = placement.RRPlacement(nodecount, nodes.NODE_CPU, nodes.NODE_MEM, nodes.DOMAIN_MEM)
        return splace.execute()
    
    
    def balance(self):
        print 'SSAPv static - not controlling'
    
