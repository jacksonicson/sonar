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
import nodes
import sys
import time
import traceback

###############################################
### CONFIG                                   ##
DEFAULT_SETUP_IP = 'vmt'
RELAY_PORT = 7900
STORAGE_POOLS = ['s0a0', 's0a1', 's1a0']
###############################################

'''
All Domains (VMs) are setup on the srv0 system! This is the initialization system. If a Domain is moved 
to another system it's configuration has to be created on the target system. 
'''

killed_vms = []
conn = None

def update_done(ret, vm, relay_conn):
    print 'Update executed'
    
    # Sometimes VMs stall while shutting down
    # Wait until VM is dead for max. 60 seconds then kill it
    new_domain = conn.lookupByName(vm)
    state = 0
    wait_time = 0
    while state != 5 and wait_time < 60:
        print state
        time.sleep(5)
        wait_time += 5
        state = new_domain.state(0)[0]
        
    if wait_time >= 60:
        print 'Killing domain %s' % (vm)
        new_domain.destroy()
        killed_vms.append(vm)
    
    # Schedule next VM clone
    reactor.callLater(0, next_vm)


def done(ret, vm):
    print 'Connection established'
    
    try:
        config = open('drones/setup_vm/main_template.sh', 'r')
        data = config.readlines()
        data = ''.join(data)
        config.close()
        
        templ = Template(data)
        d = dict(hostname=vm)
        templ = templ.substitute(d)
            
        config = open('drones/setup_vm/main.sh', 'w')
        config.writelines(templ)
        config.close()
    except Exception, e:
        print e
        reactor.stop()
        return
   
    # Rebuild drones
    drones.main()
    
    drone = drones.load_drone('setup_vm')
    
    # Do the setup process
    print 'Waiting for drone...'
    ret.launchNoWait(drone.data, drone.name).addCallback(update_done, vm, ret)
        

def error(err, vm):
    print 'Connection failed, trying again...'
    time.sleep(20)
    setup(vm)
    

def setup(vm):
    print 'Connecting...'
    # Spin (blocking) until relay is up and running
    creator = ClientCreator(reactor,
                          TTwisted.ThriftClientProtocol,
                          RelayService.Client,
                          TBinaryProtocol.TBinaryProtocolFactory(),
                          ).connectTCP(DEFAULT_SETUP_IP, RELAY_PORT)
    creator.addCallback(lambda conn: conn.client)
    
    creator.addCallback(done, vm)
    creator.addErrback(error, vm)
    

# Distribute images across all pools
pool_index = 2 # long(time.time()) % len(STORAGE_POOLS)
print 'Initial pool: %i - %s' % (pool_index, STORAGE_POOLS[pool_index])

def clone(source, target):
    # Get storage dst_pool
    pools = []
    for name in STORAGE_POOLS:
        pool = conn.storagePoolLookupByName(name)
        pools.append(pool)
    
    
    # Delete target if it exists
    try:
        print 'Undefining old domain description...'
        dom_target = conn.lookupByName(target)
        print dom_target.undefine()
        
    except:
        print 'did not remove existing domain'
        # raceback.print_exc(file=sys.stdout)
        
        
    try:
        print 'Removing old volume...'
        for delpool in pools:
            volume_target = delpool.storageVolLookupByName(target + ".qcow")
            if volume_target != None:
                print 'Deleting volume:'
                print volume_target.delete(0)
    except:
        print 'did not remove existing volume'
        # traceback.print_exc(file=sys.stdout)
    
    
    # Select pool to clone to
    global pool_index
    print 'Cloning to dst_pool: %i - %s' % (pool_index, STORAGE_POOLS[pool_index])
    dst_pool = STORAGE_POOLS[pool_index]
    dst_pool_pool = pools[pool_index]
    pool_index += 1
    
    # Load source domain
    domain = conn.lookupByName(source)
    
    # Get source pool
    xml_dom_desc = domain.XMLDesc(0)
    xml_tree = etree.fromstring(xml_dom_desc)
    name = xml_tree.xpath('/domain/devices/disk/source')
    name = name[0].get('file')
    name = name[5:9]
    src_pool_index = STORAGE_POOLS.index(name)
    src_pool = pools[src_pool_index]
    
    # Get source volume
    volume = src_pool.storageVolLookupByName(source + ".qcow")

    # Reconfigure the volume     
    xml_vol_desc = volume.XMLDesc(0)
    
    xml_tree = etree.fromstring(xml_vol_desc)
    name = xml_tree.xpath('/volume/name')[0]
    name.text = target + '.qcow'
    
    key = xml_tree.xpath('/volume/key')[0]
    key.text = '/mnt/' + dst_pool + '/' + target + '.qcow'
    
    path = xml_tree.xpath('/volume/target/path')[0]
    path.text = '/mnt/' + dst_pool + '/' + target + '.qcow'
    
    xml_vol_desc = etree.tostring(xml_tree)
    
    # Create a new volume
    print 'Cloning volume...'
    dst_pool_pool.createXMLFrom(xml_vol_desc, volume, 0)
    
    # Reconfigure the domain
    xml_domain_desc = domain.XMLDesc(0)
    
    xml_tree = etree.fromstring(xml_domain_desc)
    name = xml_tree.xpath('/domain/name')[0]
    name.text = target
    
    uuid = xml_tree.xpath('/domain/uuid')[0]
    uuid.getparent().remove(uuid)
    
    source = xml_tree.xpath('/domain/devices/disk/source')[0]
    source.set('file', '/mnt/' + dst_pool + '/' + target + '.qcow')
    
    mac = xml_tree.xpath('/domain/devices/interface/mac')[0]
    mac.getparent().remove(mac)
    
    xml_domain_desc = etree.tostring(xml_tree)
    
    # Create a new Domain
    print 'Creating Domain...'
    new_domain = conn.defineXML(xml_domain_desc)
    
    # Launch it
    print 'Starting Domain...'
    new_domain.create()
   
   
count = 0
#clone_names = [('playground', 'glassfish0'),
#               ('playground', 'glassfish1'),
#               ('playground', 'glassfish2'),
#               ('playground', 'glassfish3'),
#               ('playground', 'glassfish4'),
#               ('playground', 'glassfish5'),
#               ('playdb', 'mysql0'),
#               ('playdb', 'mysql1'),
#               ('playdb', 'mysql2'),
#               ('playdb', 'mysql3'),
#               ('playdb', 'mysql4'),
#               ('playdb', 'mysql5'), ]

clone_names = [('playglassdb', 'test%i' % i) for i in range(20, 21)]


# clone_names = [('playglassdb', 'target2')]


def next_vm():   
    global count
    
    if count >= len(clone_names):
        print 'exiting...'
        
        print 'Domains cloned'
        print ''
        print 'Following configuration steps need to be executed:'
        print '   * UPDATE: relay service'
        print '   * UPDATE: sensorhub service'
        print ''
        
        conn.close()
        reactor.stop()  
        return
    
    job = clone_names[count]
    print 'Launching job %s -> %s' % job
    count += 1
    
    clone(job[0], job[1])
    setup(job[1])


def shutdownall():
    # shutdown all VMs 
    for host in nodes.HOSTS: 
        conn_str = "qemu+ssh://root@%s/system" % (host)
        print 'connecting with %s' % (conn_str)
        conn = libvirt.open(conn_str)
        
        ids = conn.listDomainsID()
        for domain_id in ids:
            print '   Shutting down: %s' % (domain_id) 
            domain = conn.lookupByID(domain_id)
            domain.destroy()
            
        conn.close()


def main():
    # Create drones
    drones.main()
    
    # Shutdown all running VMs 
    shutdownall()
    
    print 'Cloning:'
    print clone_names
    
    print 'connecting...'
    global conn
    conn = libvirt.open("qemu+ssh://root@srv0/system")

    reactor.callLater(0, next_vm)
    reactor.run()
    

if __name__ == '__main__':
    main()
#    reactor.callLater(0, setup, 'service0')
#    reactor.run()
