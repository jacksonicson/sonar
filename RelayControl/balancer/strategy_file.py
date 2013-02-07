from control import domains
from logs import sonarlog
from virtual import nodes
import strategy
import configuration
import json

######################
# # CONFIGURATION    ##
######################
ALLOCATION_MATRIX_FILE = configuration.path('andreas_matrix_ 90_cap200', 'csv')
######################

# Setup logging
logger = sonarlog.getLogger('controller')

class Strategy(strategy.StrategyBase):
    
    def __init__(self, scoreboard, pump, model):
        super(Strategy, self).__init__(scoreboard, pump, model, 10 * 60, 120)
        self.var = []
        
    def dump(self):
        print 'Dump Sandpiper controller configuration...'
        logger.info('Strategy Configuration: %s' % json.dumps({'name' : 'File',
                                                                 'allocation_matrix_file' : ALLOCATION_MATRIX_FILE,
                                                                 }))
    

    def initial_placement(self):
        nodecount = len(nodes.NODES)
        domaincount = len(domains.domain_profile_mapping)
        
        # Read allocation matrix
        handle = open(ALLOCATION_MATRIX_FILE, 'r')
        lines = handle.readlines()
        handle.close()
        
        # Rows are servers, columns are domains
        active_servers = 0
        matrix = [[0 for _ in xrange(domaincount)] for _ in xrange(nodecount)]
        for x, line in enumerate(lines):
            elements = line.split(',')
            
            x_active = False
            
            for y, element in enumerate(elements):
                matrix[x][y] = int(element)
                
                if matrix[x][y] > 0:
                    x_active = True
                    
            if x_active:
                active_servers += 1
                
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
        return migrations, active_servers
    
    def balance(self):
        # print 'SSAPv static - not controlling'
        pass
    
