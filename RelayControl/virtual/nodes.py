'''
List of all hosts/nodes in the infrastructure
'''
NODES = HOSTS = ['srv0', 'srv1', 'srv2', 'srv3', 'srv4', 'srv5']
NODE_MEM = 15*1024 # MByte (available memory of the node estimated)
DOMAIN_MEM = 2048 + 100 # MByte (domain memory  + KVM overhead estimated)
NODE_CPU = 200

def dump():
    print 'NODES = HOSTS = %s' % NODES
    print 'NODE_MEM = %i' % NODE_MEM
    print 'DOMAIN_MEM = %i' % DOMAIN_MEM
    print 'NODE_CPU = %i' % NODE_CPU