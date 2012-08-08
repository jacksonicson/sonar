from control import drones, hosts
from datetime import datetime
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


###############################################
### CONFIG                                   ##
RELAY_PORT = 7900
###############################################

hosts = ['srv0', 'srv1', 'srv2', 'srv3', 'srv4', 'srv5']

allocation = [ ('glassfish0', 0),
               ('glassfish1', 1),
               ('glassfish2', 2),
               ('glassfish3', 3),
               ('glassfish4', 4),
               ('glassfish5', 5),
               ('mysql0', 0),
               ('mysql1', 1),
               ('mysql2', 2),
               ('mysql3', 3),
               ('mysql4', 4),
               ('mysql5', 5), ]



def main():
    connections = []
    
    # shutdown all VMs 
    for host in hosts: 
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
        # Setup initial allocation
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
        

if __name__ == '__main__':
    main()
