from control.domains import domain_profile_mapping as mapping
from libvirt import VIR_MIGRATE_LIVE, VIR_MIGRATE_UNDEFINE_SOURCE, \
    VIR_MIGRATE_PERSIST_DEST
import libvirt
import nodes
import sys
import time
import traceback
import control.domains as domains
from threading import Thread

###############################################
### CONFIG                                   ##
RELAY_PORT = 7900
###############################################

# Error handler for libvirt
def handler(ctxt, err):
    print 'Libvirt error'
    print err
    print ctxt
    
libvirt.registerErrorHandler(handler, 'context') 

def __find_domain(connections, domain_name):
    last = None, None
    for connection in connections:
        try:
            domain = connection.lookupByName(domain_name)
            last = domain, connection
            
            state = domain.state(0)[0]
            if state == 1:
                return domain, connection
        except:
            pass
        
    return last


connections = []

def connect_all():
    # connect 
    global connections  
    for host in nodes.HOSTS: 
        conn_str = "qemu+ssh://root@%s/system" % (host)
        print 'connecting with %s' % (conn_str)
        conn = libvirt.open(conn_str)
        connections.append(conn)
        
    return connections


def close_all():
    print 'Closing libvirtd connections...'
    global connections
    for connection in connections:
        connection.close()

class MigrationThread(Thread):
    def __init__(self, domain, node_from, node_to, callback, info):
        super(MigrationThread, self).__init__()
        self.domain = domain
        self.node_from = node_from
        self.node_to = node_to
        self.callback = callback
        self.info = info
    
    def run(self):
        self.start = time.time()
        connection_from = libvirt.open("qemu+ssh://root@%s/system" % self.node_from) 
        domain = connection_from.lookupByName(self.domain)
        connection_to = libvirt.open("qemu+ssh://root@%s/system" % self.node_to) 
        
        try:
            self.tomigrate = domain
            domain = domain.migrate(connection_to, VIR_MIGRATE_LIVE | VIR_MIGRATE_UNDEFINE_SOURCE | VIR_MIGRATE_PERSIST_DEST, self.domain, None, 0)
            self.end = time.time()
            
            print 'Calling back...'
            self.callback(self.domain, self.node_from, self.node_to, self.start, self.end, self.info, True, None)
        except Exception as e:
            self.end = time.time()
            
            print 'Error in live migration'
            traceback.print_exc(file=sys.stdout)
            self.callback(self.domain, self.node_from, self.node_to, self.start, self.end, self.info, False, e)
        finally:
            # Close connections
            try:
                connection_from.close()
            except: pass
            try:
                connection_to.close()
            except: pass
                


# connections = None

def migrateDomain(domain, node_from, node_to, callback, info=None, maxDowntime=20000):
    thread = MigrationThread(domain, node_from, node_to, callback, info)
    thread.start()
    while True:
        time.sleep(1)
        try:
            thread.tomigrate.migrateSetMaxDowntime(maxDowntime, 0)
            print 'Max migration time set to %i' % maxDowntime
            break
        except:
            pass
    

def migrateAllocation(allocation):
    connections = []
    conn_strs = []
    try:
        # connect 
        for host in nodes.HOSTS: 
            conn_str = "qemu+ssh://root@%s/system" % (host)
            print 'connecting with %s' % (conn_str)
            conn = libvirt.open(conn_str)
            connections.append(conn)
            conn_strs.append(conn_str)
        
        # trigger migrations
        for migration in allocation:
            print 'iteration'
            domain_name = migration[0]
            target_index = migration[1]
            
            domain, src_conn = __find_domain(connections, domain_name)
            if domain == None:
                print 'Domain not found: %s' % (domain_name)
                continue
            
            xml_desc = domain.XMLDesc(0)
            
            # if not running start on source (necessary for migrations?)
            state = domain.state(0)[0]
            print 'domain state: %i' % (state)
            if state != 1: 
                # stop domain
                print 'resetting domain %s' % (domain_name)
                try:
                    domain.destroy()
                except: pass
                # start domain
                try:
                    domain.create()
                    time.sleep(10)
                except: pass
            
            # remove xml desc from target if exists
            try:
                dom_target = connections[target_index].lookupByName(domain_name)
                dom_target.undefine()
                print 'successful undefined target'
            except:
                pass
            
            # migrate to target
            try:
                print 'migrating %s -> %s ...' % (domain_name, connections[target_index].getHostname())
                # domain = domain.migrate2(connections[target_index], xml_desc, VIR_MIGRATE_LIVE, domain_name, None, 0)
                domain = domain.migrate(connections[target_index], VIR_MIGRATE_LIVE | VIR_MIGRATE_UNDEFINE_SOURCE | VIR_MIGRATE_PERSIST_DEST, domain_name, None, 0)
                domain.migrateSetMaxDowntime(3000, 0)
                print 'done'
            except:
                traceback.print_exc(file=sys.stdout)
                print 'passed'
            
    except:
        # print 'error while executing migrations: %s' % errno[2]
        traceback.print_exc(file=sys.stdout)
        pass

    for conn in connections:
        print 'closing connection...'
        conn.close()
        

def resetAllocation(allocation):
    connections = []
    
    # shutdown all VMs 
    for host in nodes.HOSTS: 
        conn_str = "qemu+ssh://root@%s/system" % (host)
        print 'connecting with %s' % (conn_str)
        conn = libvirt.open(conn_str)
        connections.append(conn)
        
        ids = conn.listDomainsID()
        for domain_id in ids:
            print '   Shutting down: %s' % (domain_id) 
            domain = conn.lookupByID(domain_id)
            domain.destroy()
    
    try:
        # Setup allocation
        for migration in allocation:
            domain_name = migration[0]
            target_index = migration[1]
            
            # Check if target host has the VM description
            print domain_name
            print target_index
            domain = None
            try:
                domain = connections[target_index].lookupByName(domain_name)
            except:
                print 'Defining domain...'
                domain = connections[0].lookupByName(domain_name)
                xml_desc = domain.XMLDesc(0)
                domain = connections[target_index].defineXML(xml_desc)
                
            # Launch domain
            print 'Launching domain...'
            domain.create()
            
            
    except Exception, e:
        print e
            
    
    for conn in connections:
        print 'closing connection...'
        conn.close()

def get_null_allocation(nodecount):
    migrations = []
    assignment = {}
    
    node_index = 0
    service_index = 0
    for maps in mapping:
        migrations.append((maps.domain, node_index))
        node_index = (node_index + 1) % nodecount
        
        assignment[service_index] = node_index
        service_index += 1
        
    return assignment, migrations


def determine_current_allocation():
    # Connect with all servers
    connections = [] 
    for host in nodes.HOSTS: 
        conn_str = "qemu+ssh://root@%s/system" % (host)
        print 'connecting with %s' % (conn_str)
        conn = libvirt.open(conn_str)
        connections.append(conn)
        
    allocation = { host : [] for host in nodes.HOSTS }
        
    for i in xrange(len(nodes.HOSTS)):
        host = nodes.HOSTS[i]
        connection = connections[i]
        
        # print 'Host: %s' % host
        
        vir_domains = connection.listDomainsID()
        for vir_id in vir_domains:
            vir_domain = connection.lookupByID(vir_id)
            name = vir_domain.name()
            if domains.has_domain(name):
                # print 'adding mapping with %s' % name
                allocation[host].append(name)
            else:
                print 'ERROR: Domain %s is not in the domain list!' % name
            
    print 'Closing connections...'
    for connection in connections:
        connection.close()       
    
    return allocation
    
    
    
def migrationtest():
    connections = []
    
    # shutdown all VMs 
    for host in nodes.HOSTS: 
        conn_str = "qemu+ssh://root@%s/system" % (host)
        print 'connecting with %s' % (conn_str)
        conn = libvirt.open(conn_str)
        connections.append(conn)
 
    domain_name = 'target1'
    target_index = 3
    domain, src_conn = __find_domain(connections, domain_name)
    if domain == None:
        print 'Domain not found: %s' % (domain_name)
        return
            
    xml_desc = domain.XMLDesc(0)
            
    # if not running start on source (necessary for migrations?)
    state = domain.state(0)[0]
    print 'domain state: %i' % (state)
    if state != 1: 
        # stop domain
        print 'resetting domain %s' % (domain_name)
        try:
            domain.destroy()
        except: pass
        
        # start domain
        try:
            domain.create()
            time.sleep(10)
        except: pass
            
    # remove xml desc from target if exists
    try:
        dom_target = connections[target_index].lookupByName(domain_name)
        dom_target.undefine()
        print 'successful undefined target'
    except:
        pass
            
    # migrate to target
    try:
        print 'migrating %s -> %s ...' % (domain_name, connections[target_index].getHostname())
        # domain = domain.migrate2(connections[target_index], xml_desc, VIR_MIGRATE_LIVE, domain_name, None, 0)
        
        domain = domain.migrate(connections[target_index], VIR_MIGRATE_LIVE | VIR_MIGRATE_UNDEFINE_SOURCE, domain_name, None, 0)
        
        print 'done'
    except:
        global errno
        print 'passed: %s' % (errno[2])
 
 
    for conn in connections:
        print 'closing connection...'
        conn.close()
 
if __name__ == '__main__':
    # migrationtest()
    determine_current_allocation()
    pass
