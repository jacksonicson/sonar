from ipmodels import ssapv, dsap
from logs import sonarlog
from service import times_client
from virtual import allocation as virt, nodes
from workload import profiles
import domains
import numpy as np
from logic import placement

# Setup logging
logger = sonarlog.getLogger('allocate_domains')

def main(migrate=True):
    nodecount = len(nodes.HOSTS)
    
    # Setup models
    model = placement.SSAPvPlacement(nodecount, nodes.NODE_CPU, nodes.NODE_MEM, nodes.DOMAIN_MEM)
    # model = placement.RRPlacement(nodecount, nodes.NODE_CPU, nodes.NODE_MEM, nodes.DOMAIN_MEM)
    
    # Get migrations
    migrations = model.execute()
    
    # Migrate
    if migrate:
            print 'Migrating...'
            virt.migrateAllocation(migrations)

if __name__ == '__main__':
    main()

