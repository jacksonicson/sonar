'''
All Domains (VMs) are setup on the srv0 system! This is the initialization system. If a Domain is moved 
to another system it's configuration has to be created on the target system. 
'''

from control import drones
from lxml import etree
from relay import RelayService
from string import Template
from thrift.protocol import TBinaryProtocol
from thrift.transport import TTwisted
from twisted.internet import reactor
from twisted.internet.protocol import ClientCreator
import nodes
import sys
import time
import traceback
import virtual.util as util

###############################################
### CONFIG                                   ##
###############################################
DEFAULT_SETUP_IP = 'vmt'
RELAY_PORT = 7900
STORAGE_POOLS = ['s0a0', 's0a1', 's1a0']
clone_names = [('playglassdb', 'target%i' % i) for i in range(0, 18)]
SETUP_SERVER = 'srv0'
###############################################


killed_vms = []
connections = None 

def update_done(ret, vm, relay_conn):
    print 'Update executed'
    
    # Sometimes VMs stall while shutting down
    # Wait until VM is dead for max. 60 seconds then kill it
    conn = connections[SETUP_SERVER]
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


def connection_established(ret, vm):
    print 'Connection established'
    
    try:
        # Read configuration template
        config = open('drones/setup_vm/main_template.sh', 'r')
        data = config.readlines()
        data = ''.join(data)
        config.close()
        
        # Templating engine
        templ = Template(data)
        d = dict(hostname=vm)
        templ = templ.substitute(d)
            
        # Write result configuration
        config = open('drones/setup_vm/main.sh', 'w')
        config.writelines(templ)
        config.close()
    except Exception, e:
        traceback.print_exc(file=sys.stdout)
        reactor.stop()
        return
   
    # Rebuild drones
    drones.main()
    
    # Load and execute drone
    print 'Waiting for drone...'
    drone = drones.load_drone('setup_vm')
    ret.launchNoWait(drone.data, drone.name).addCallback(update_done, vm, ret)
        

def error(err, vm):
    print 'Connection failed, waiting and trying again...'
    reactor.callLater(20, setup, vm)
    

def setup(vm):
    print 'Connecting with new domain...'
    
    creator = ClientCreator(reactor,
                          TTwisted.ThriftClientProtocol,
                          RelayService.Client,
                          TBinaryProtocol.TBinaryProtocolFactory(),
                          ).connectTCP(DEFAULT_SETUP_IP, RELAY_PORT)
    creator.addCallback(lambda conn: conn.client)
    
    creator.addCallback(connection_established, vm)
    creator.addErrback(error, vm)
    

def rand_mac():
    import random
    base = '52:54:00'
    # generate 3 random NN blocks
    for i in xrange(3):
        rand = random.randint(0, 255)
        value = hex(rand)[2:]
        base += ':' + value
    
    return base

# Distribute images across all pools, pool_index gives the pool where the next
# VM will be created
pool_index = long(time.time()) % len(STORAGE_POOLS)
print 'Initial pool: %i - %s' % (pool_index, STORAGE_POOLS[pool_index])

def clone(connections, source, target):
    # Connection for srv0
    conn = connections[SETUP_SERVER]
    
    # Connect with all known storage pools
    print 'Connecting with storage pools...'
    pools = []
    for name in STORAGE_POOLS:
        pool = conn.storagePoolLookupByName(name)
        pools.append(pool)
    
    # Delete target if it exists
    print 'Remove old domain description...'
    for host in nodes.HOSTS:
        try:
            dom_target = connections[host].lookupByName(target)
            if dom_target != None:
                ret = dom_target.undefine()
                print 'Domain removed: %i' % ret 
        except:
            pass
        
        
    print 'Removing old volume...'
    for delpool in pools:
        try:
            volume_target = delpool.storageVolLookupByName(target + ".qcow")
            if volume_target != None:
                ret = volume_target.delete(0)
                print 'Volume removed: %i' % ret
        except:
            pass
    
    
    # Select pool to clone to
    global pool_index
    print 'Cloning to dst_pool: %i - %s' % (pool_index, STORAGE_POOLS[pool_index])
    dst_pool = STORAGE_POOLS[pool_index]
    dst_pool_pool = pools[pool_index]
    pool_index = (pool_index + 1) % len(STORAGE_POOLS)
    
    # Load source domain
    source_domain = conn.lookupByName(source)
    
    # Get source pool
    xml_dom_desc = source_domain.XMLDesc(0)
    xml_tree = etree.fromstring(xml_dom_desc)
    name = xml_tree.xpath('/domain/devices/disk/source')
    name = name[0].get('file')
    name = name[5:9]
    src_pool_index = STORAGE_POOLS.index(name)
    src_pool = pools[src_pool_index]
    
    # Get source volume
    volume = src_pool.storageVolLookupByName(source + ".qcow")

    # Reconfigure the volume description    
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
    
    # Reconfigure the domain description
    xml_domain_desc = source_domain.XMLDesc(0)
    print xml_domain_desc
    
    xml_tree = etree.fromstring(xml_domain_desc)
    name = xml_tree.xpath('/domain/name')[0]
    name.text = target
    uuid = xml_tree.xpath('/domain/uuid')[0]
    uuid.getparent().remove(uuid)
    source = xml_tree.xpath('/domain/devices/disk/source')[0]
    source.set('file', '/mnt/' + dst_pool + '/' + target + '.qcow')
    mac = xml_tree.xpath('/domain/devices/interface/mac')[0]
    mac.attrib['address'] = rand_mac()
    xml_domain_desc = etree.tostring(xml_tree)
    
    print xml_domain_desc
    
    # Create a new Domain
    print 'Creating domain...'
    new_domain = conn.defineXML(xml_domain_desc)
    
    # Launch domain
    print 'Launching Domain...'
    new_domain.create()
   
   
# VM clone counter
count = 0

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
        
        reactor.stop()  
        return
    
    job = clone_names[count]
    print 'Launching clone %s -> %s' % job
    count += 1
    
    clone(connections, job[0], job[1])
    setup(job[1])


def shutdownall():
    for host in nodes.HOSTS: 
        conn = connections[host]
        ids = conn.listDomainsID()
        for domain_id in ids:
            print '   Shutting down: %s' % (domain_id) 
            domain = conn.lookupByID(domain_id)
            domain.destroy()


def main():
    # Dump configuration
    print 'Cloning: %s ' % clone_names
    
    # Create drones
    drones.main()
    
    # Connect
    global connections
    connections = util.connect_all()
    
    try:
        # Shutdown all running VMs 
        shutdownall()
        
        reactor.callLater(0, next_vm)
        
        print 'Starting reactor'
        reactor.run()
        print 'Reactor returned'
        
    finally:
        util.close_all(connections)
    

if __name__ == '__main__':
    main()
