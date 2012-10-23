from logic import placement
from logs import sonarlog
from virtual import allocation as virt, nodes
import time
import json

# Setup logging
logger = sonarlog.getLogger('allocate_domains')

def main(migrate=True):
    nodecount = len(nodes.HOSTS)
    
    # Setup models
    # model = placement.SSAPvPlacement(nodecount, nodes.NODE_CPU, nodes.NODE_MEM, nodes.DOMAIN_MEM)
    # model = placement.RRPlacement(nodecount, nodes.NODE_CPU, nodes.NODE_MEM, nodes.DOMAIN_MEM)
    model = placement.FirstFitPlacement(nodecount, nodes.NODE_CPU, nodes.NODE_MEM, nodes.DOMAIN_MEM)
    
    # Get migrations
    migrations, active_server_info  = model.execute()
    
    print 'Updated active server count: %i' % active_server_info[0]
    logger.info('Initial Active Servers: %s' % json.dumps({'count' : active_server_info[0],
                                                           'servers: ' : active_server_info[1],
                                                           'timestamp' : time.time()}))
    
    # Migrate
    if migrate:
            print 'Migrating...'
            virt.migrateAllocation(migrations)


if __name__ == '__main__':
    main(True)

