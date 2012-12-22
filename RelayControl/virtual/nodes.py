'''
List of all hosts/nodes in the infrastructure
'''

NODES = []
for i in xrange(30):
    NODES.append('srv%i' % i)
HOSTS = NODES
    
NODE_CPU_CORES = 4
DOMAIN_CPU_CORES = 2
NODE_MEM = 31 * 1024 # MByte (available memory of the node estimated)
DOMAIN_MEM = 400 + 100 # MByte (domain memory  + KVM overhead estimated)
NODE_CPU = 230 # Has space for two dual core VMs

###############################################################################
###############################################################################

def get_node_name(index):
    return NODES[index]

def cpu_factor():
    return NODE_CPU_CORES / DOMAIN_CPU_CORES

def dump(logger):
    logger.info('NODES = HOSTS = %s' % NODES)
    logger.info('NODE_MEM = %i' % NODE_MEM)
    logger.info('DOMAIN_MEM = %i' % DOMAIN_MEM)
    logger.info('NODE_CPU = %i' % NODE_CPU)
    
def to_node_load(domain_load):
    return domain_load / (NODE_CPU_CORES / DOMAIN_CPU_CORES)


def count():
    return len(NODES)
    
