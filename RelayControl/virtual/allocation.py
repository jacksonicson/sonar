from control import drones, hosts
from datetime import datetime
from libvirt import VIR_MIGRATE_LIVE
from lxml import etree
from rain import RainService, constants, ttypes
from relay import RelayService
from string import Template
from thrift import Thrift, Thrift
from thrift.protocol import TBinaryProtocol, TBinaryProtocol
from thrift.transport import TSocket, TTransport, TTwisted
from twisted.internet import defer, reactor
from twisted.internet.defer import inlineCallbacks
from twisted.internet.protocol import ClientCreator
import libvirt
import nodes
import traceback
import sys
import time


###############################################
### CONFIG                                   ##
RELAY_PORT = 7900
###############################################

# Error handler for libvirt
def handler(ctxt, err):
    global errno
    errno = err
libvirt.registerErrorHandler(handler, 'context') 

def __find_domain(connections, domain_name):
    for connection in connections:
        try:
            domain = connection.lookupByName(domain_name)
            return domain, connection
        except:
            pass
        
    return None, None

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
            domain_name = migration[0]
            target_index = migration[1]
            
            domain, src_conn = __find_domain(connections, domain_name)
            if domain == None:
                print 'Domain not found: %s' % (domain_name)
                continue
            
            xml_desc = domain.XMLDesc(0)
            
            # if not running start on target
            state = domain.state(0)[0]
            print 'domain state: %i' % (state)
            if state != 1: 
                print 'resetting domain %s' % (domain_name)
                try:
                    domain.destroy()
                except: pass
                try:
                    domain.create()
                    time.sleep(10)
                except: pass
            
            # migrate to target
            try:
                print 'migrating %s -> %s ...' % (domain_name, connections[target_index].getHostname())
                domain = domain.migrate2(connections[target_index], xml_desc, VIR_MIGRATE_LIVE, domain_name, None, 100)
                print 'done'
            except:
                global errno
                print 'passed: %s' % (errno[2])
            
    except:
        print 'error while executing migrations: %s' % errno[2]
        traceback.print_exc(file=sys.stdout)

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

def get_null_allocation():
    allocation = []
    node_index = 0
    for maps in mapping:
        allocation.append((maps.domain, node_index))
        node_index = (node_index + 1) % len(nodes.HOSTS)
        
    return allocation

def main():
    print 'Distributing domains over all servers ...'
    from control.domains import domain_profile_mapping as mapping
    
    allocation = get_null_allocation()
    print allocation
    
    # migrateAllocation(allocation)    
    resetAllocation(allocation)
 
if __name__ == '__main__':
    main()
