import nodes
import libvirt

def connect_all():
    connections = {}
    for host in nodes.HOSTS: 
        conn_str = "qemu+ssh://root@%s/system" % (host)
        print 'connecting with %s' % (conn_str)
        conn = libvirt.open(conn_str)
        connections[host] = conn
        
    return connections


def close_all(connections):
    print 'Closing libvirtd connections...'
    for connection in connections.values():
        connection.close()