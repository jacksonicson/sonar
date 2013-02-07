from logs import sonarlog
import controller
import json

######################
## CONFIGURATION    ##
######################
######################

# Setup logging
logger = sonarlog.getLogger('controller')

class Controller(controller.LoadBalancer):
    
    def __init__(self, scoreboard, pump, model):
        super(Controller, self).__init__(scoreboard, pump, model, 10*60, 120)
        self.var = []
        
    def dump(self):
        print 'Dump Sandpiper controller configuration...'
        logger.info('Controller Configuration: %s' % json.dumps({'name' : 'SSAPv',
                                                                 }))
    
    def initial_placement(self):
        from virtual import placement
        from virtual import nodes
        from control import domains 
        
        nodecount = len(nodes.NODES)
        splace = placement.RRPlacement(nodecount, nodes.NODE_CPU, nodes.NODE_MEM, nodes.DOMAIN_MEM)
        migrations, _ = splace.execute()
        
        _nodes = []
        for node in nodes.NODES: 
            mnode = self.model.Node(node, nodes.NODE_CPU_CORES)
            _nodes.append(mnode)
            
        _domains = {}
        for domain in domains.domain_profile_mapping:
            dom = self.model.Domain(domain.domain, nodes.DOMAIN_CPU_CORES)
            _domains[domain.domain] = dom
            
        for migration in migrations:
            print migration 
            _nodes[migration[1]].add_domain(_domains[migration[0]])
            
        return migrations, nodecount
    
    
    def balance(self):
        print 'SSAPv static - not controlling'
    
