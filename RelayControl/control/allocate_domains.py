from logs import sonarlog
from virtual import allocation as virt, nodes, placement
import json
import time

# Setup logging
logger = sonarlog.getLogger('allocate_domains')

def main(migrate=True):
    nodecount = len(nodes.NODES)
    
    # Setup models
    # model = placement.SSAPvPlacement(nodecount, nodes.NODE_CPU, nodes.NODE_MEM, nodes.DOMAIN_MEM)
    # model = placement.RRPlacement(nodecount, nodes.NODE_CPU, nodes.NODE_MEM, nodes.DOMAIN_MEM)
    # model = placement.FirstFitPlacement(nodecount, nodes.NODE_CPU, nodes.NODE_MEM, nodes.DOMAIN_MEM)
    
    # Get migrations
    # migrations, active_server_info  = model.execute()
    
    import balancer.main as controller
    migrations, active_server_info = controller.initial_allocation() 
    
    print 'Updated active server count: %i' % active_server_info[0]
    logger.info('Initial Active Servers: %s' % json.dumps({'count' : active_server_info[0],
                                                           'servers' : active_server_info[1],
                                                           'timestamp' : time.time()}))
    
    # Migrate
    if migrate:
            print 'Migrating...'
            virt.migrateAllocation(migrations)


if __name__ == '__main__':
    main(True)

