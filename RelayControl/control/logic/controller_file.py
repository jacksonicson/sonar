from control import domains
from logs import sonarlog
from virtual import nodes, placement
import configuration
import controller
import json

######################
## CONFIGURATION    ##
######################
ALLOCATION_MATRIX_FILE = configuration.path('andreas_matrix_180_I_181_bis_360_cap_230', 'csv')
######################

# Setup logging
logger = sonarlog.getLogger('controller')

class Sandpiper(controller.LoadBalancer):
    
    def __init__(self, pump, model):
        super(Sandpiper, self).__init__(pump, model, 10 * 60, 120)
        self.var = []
        
    def dump(self):
        print 'Dump Sandpiper controller configuration...'
        logger.info('Controller Configuration: %s' % json.dumps({'name' : 'File',
                                                                 'allocation_matrix_file' : ALLOCATION_MATRIX_FILE,
                                                                 }))
    # Initial placement calculation (simulation only!!!)
    def initial_placement_sim(self):
        nodecount = len(nodes.HOSTS)
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
    
