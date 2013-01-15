from control import domains
from logs import sonarlog
from virtual import nodes
import configuration
import controller
import json

######################
## CONFIGURATION    ##
######################
ALLOCATION_MATRIX_FILE = configuration.path('andreas_matrix_I90_VM91-180_compliance_0.99_cap_230_servers12', 'csv')
######################

# Setup logging
logger = sonarlog.getLogger('controller')

class Controller(controller.LoadBalancer):
    
    def __init__(self, scoreboard, pump, model):
        super(Controller, self).__init__(scoreboard, pump, model, 10 * 60, 120)
        self.var = []
        
    def dump(self):
        print 'Dump Sandpiper controller configuration...'
        logger.info('Controller Configuration: %s' % json.dumps({'name' : 'File',
                                                                 'allocation_matrix_file' : ALLOCATION_MATRIX_FILE,
                                                                 }))
    # Initial placement calculation (simulation only!!!)
    def initial_placement_sim(self):
        nodecount = len(nodes.NODES)
        domaincount = len(domains.domain_profile_mapping)
        
        # Read allocation matrix
        handle = open(ALLOCATION_MATRIX_FILE, 'r')
        lines = handle.readlines()
        handle.close()
        
        # Rows are servers
        # Columns are domains
        matrix = [[0 for _ in xrange(domaincount)] for _ in xrange(nodecount)]
        for x, line in enumerate(lines):
            elements = line.split(',')
            for y, element in enumerate(elements):
                matrix[x][y] = int(element)
                
        # Convert allocation matrix to a migration list
        migrations = []
        for inode in xrange(len(matrix)):
            for idomain in xrange(len(matrix[inode])):
                if matrix[inode][idomain] > 0:
                    mapping = domains.domain_profile_mapping[idomain]
                    migration = (mapping.domain, inode)
                    migrations.append(migration)

        # Log migrations
        print 'Migrations: %s' % migrations
        
        # Build internal model 
        self.build_internal_model(migrations)
        return migrations
    
    def balance(self):
        # print 'SSAPv static - not controlling'
        pass
    
