'''
List of all hosts/nodes in the infrastructure
'''

# Nodes
NODES = []
for i in xrange(30):
    NODES.append('srv%i' %i)
HOSTS = NODES

# Node hardware configuration
NODE_CPU_CORES = 4
DOMAIN_CPU_CORES = 2
NODE_MEM = 15*1024 # MByte (available memory of the node estimated)
DOMAIN_MEM = 2048 + 100 # MByte (domain memory  + KVM overhead estimated)
NODE_CPU = 230 # Has space for two dual core VMs

###############################################################################
###############################################################################

def get_node_name(index):
    return NODES[index]

def dump(logger):
    logger.info('NODES = HOSTS = %s' % NODES)
    logger.info('NODE_MEM = %i' % NODE_MEM)
    logger.info('DOMAIN_MEM = %i' % DOMAIN_MEM)
    logger.info('NODE_CPU = %i' % NODE_CPU)