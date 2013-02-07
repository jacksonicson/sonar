from logs import sonarlog
from virtual import allocation as virt
import balancer.control_manager as controller
import json
import time

# Setup logging
logger = sonarlog.getLogger('allocate_domains')

def allocate_domains(migrate, controller):
    # Calculate initial placement
    migrations, active_server_info = controller.strategy.initial_allocation() 

    # Log initial placement settings    
    print 'Updated active server count: %i' % active_server_info[0]
    logger.info('Initial Active Servers: %s' % json.dumps({'count' : active_server_info[0],
                                                           'servers' : active_server_info[1],
                                                           'timestamp' : time.time()}))
    
    # Trigger migrations
    if migrate:
            print 'Migrating...'
            virt.migrateAllocation(migrations)


if __name__ == '__main__':
    controller = controller.build_controller()
    allocate_domains(True, controller)

