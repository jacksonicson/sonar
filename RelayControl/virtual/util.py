import nodes
import libvirt

def connect(node):
    try:
        print 'connecting with %s' % node
        conn_str = "qemu+ssh://root@%s/system" % (node)
        print 'connecting with %s' % (conn_str)
        conn = libvirt.open(conn_str)
        return conn
    except:
        print 'failed connecting with node %s' % node
        return None


def close(connection):
    try:
        print 'Closing libvirtd connection...'
        connection.close()
    except:
        print 'failed disconnecting'


def connect_all():
    connections = {}
    for node in nodes.NODES: 
        conn_str = "qemu+ssh://root@%s/system" % (node)
        print 'connecting with %s' % (conn_str)
        conn = libvirt.open(conn_str)
        connections[node] = conn
        
    return connections


def close_all(connections):
    print 'Closing libvirtd connections...'
    for connection in connections.values():
        connection.close()