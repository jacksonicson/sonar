'''
All Domains (VMs) are configure_domain on the srv0 system! This is the initialization system. If a Domain is moved 
to another system it's configuration has to be created on the target system. 
'''

from control import drones
from lxml import etree
from relay import RelayService
from string import Template
from thrift.protocol import TBinaryProtocol
from thrift.transport import TTwisted
from twisted.internet import defer, reactor
from twisted.internet.defer import DeferredQueue
from twisted.internet.protocol import ClientCreator
import configuration as config
import nodes
import sys
import threading
import time
import traceback
import virtual.util as util

###############################################
# ## CONFIG                                   ##
###############################################
DEFAULT_SETUP_IP = 'vmt'
STORAGE_POOLS = ['s0a0', 's0a1', 's1a0']
clone_names = [('playglassdb_v2', 'target%i' % i) for i in range(0, 18)]
SETUP_SERVER = 'srv0'
###############################################


exit_name = None
killed_vms = []
connections = None
queue = DeferredQueue()

# Distribute images across all pools, pool_index gives the pool where the next VM will be created
pool_index = long(time.time()) % len(STORAGE_POOLS)
 
 
class QueueEntry(object):
    '''
    Describes one clone entry in the clone queue
    '''
    
    def __init__(self, source, target, domain_id):
        self.source = source
        self.target = target
        self.domain_id = domain_id  


def domain_configuration_finished(target):
    '''
    Is called as soon as a domain is fully configured. 
    '''
    
    if target is exit_name:
        print 'Exiting...'
        stop()
        return
    
    print 'Domain cloned successfully'
    wait_for_next_entry()


def kill_domain(ret, vm, relay_conn):
    '''
    Waits until a domain is shut down. After a timeout the domain 
    gets killed.
    '''
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
    
    # Finish
    domain_configuration_finished(vm)
    


def launch_drone(ret, vm):
    '''
     Launches the drone on the connection in the parameter
    '''
    
    print 'Launching drone (connection established)'
    
    try:
        # Read configuration template
        config = open(drones.DRONE_DIR + '/setup_vm/main_template.sh', 'r')
        data = config.readlines()
        data = ''.join(data)
        config.close()
        
        # Templating engine
        templ = Template(data)
        d = dict(hostname=vm)
        templ = templ.substitute(d)
            
        # Write result configuration
        config = open(drones.DRONE_DIR + '/setup_vm/main.sh', 'w')
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
    ret.launchNoWait(drone.data, drone.name).addCallback(kill_domain, vm, ret)
        

def error(err, vm):
    '''
    Error handler if the connection with the new domain fails
    '''
    sys.stdout.write('.')
    reactor.callLater(3, configure_domain, vm)
    

def configure_domain(target):
    '''
    Reconfigures a domain by running the reconfiguration drone 
    '''
    
    print 'Connecting with new domain.'
    creator = ClientCreator(reactor,
                          TTwisted.ThriftClientProtocol,
                          RelayService.Client,
                          TBinaryProtocol.TBinaryProtocolFactory(),
                          ).connectTCP(DEFAULT_SETUP_IP, config.RELAY_PORT, timeout=10)
    creator.addCallback(lambda conn: conn.client)
    creator.addCallback(launch_drone, target)
    creator.addErrback(error, target)
    

def mac_by_id(domain_id):
    '''
    Is used to give target0 always the same MAC for each clone_domain process. 
    If random MACs are used the DNS server registers multiply mappings and cannot
    resolve the names properly. 
    '''
    
    base = '52:54:00'
    # generate 3 0xNN blocks
    for i in xrange(3):
        rand = domain_id
        value = hex(rand)[2:]
        if len(value) == 1:
            value = '0' + value
        base += ':' + value

    print 'By ID generated MAC: %s' % base    
    return base


def mac_by_rand():
    '''
    Generates a MAC address based on a random number
    '''
    
    import random
    base = '52:54:00'
    # generate 3 random NN blocks
    for i in xrange(3):
        rand = random.randint(0, 255)
        value = hex(rand)[2:]
        if len(value) == 1:
            value = '0' + value
        base += ':' + value

    print 'Randomly generated MAC: %s' % base    
    return base



def clone_domain(connections, source, target, domain_id):
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
    for host in nodes.NODES:
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
    # print xml_domain_desc # print original domain description
    
    xml_tree = etree.fromstring(xml_domain_desc)
    name = xml_tree.xpath('/domain/name')[0]
    name.text = target
    uuid = xml_tree.xpath('/domain/uuid')[0]
    uuid.getparent().remove(uuid)
    source = xml_tree.xpath('/domain/devices/disk/source')[0]
    source.set('file', '/mnt/' + dst_pool + '/' + target + '.qcow')
    mac = xml_tree.xpath('/domain/devices/interface/mac')[0]
    mac.attrib['address'] = mac_by_id(domain_id)
    xml_domain_desc = etree.tostring(xml_tree)
    # print xml_domain_desc # print final domain description
    
    # Create a new Domain
    print 'Creating domain...'
    new_domain = conn.defineXML(xml_domain_desc)
    
    # Launch domain
    print 'Launching Domain...'
    new_domain.create()
 
 
def wait_for_next_entry():
    # Register callback handler again to handle the next entry
    d = queue.get() 
    d.addCallback(next_clone_entry)
 
 
def next_clone_entry(entry):
    print 'processing next clone entry in queue...'
    
    # Clone the domain
    clone_domain(connections, entry.source, entry.target, entry.domain_id)
    
    # Configure the domain
    configure_domain(entry.target)

def stop():
    reactor.stop()

def start_reactor():
    class ThreadWrapper(threading.Thread):
        def run(self):
            reactor.run(installSignalHandlers=0)
            
    thr = ThreadWrapper()
    thr.start()
    return thr

def start():
    print 'Rebuilding drones...'
    # Create drones
    drones.main()
    
    # Connect
    print 'Connecting with libvirt daemons...'
    global connections
    connections = util.connect_all()
    
    # Start queue listener
    wait_for_next_entry()
    
    # Start reactor 
    print 'Starting reactor in a new thread...'
    return start_reactor()
 
 
def shutdownall():
    # Go over all nodes
    for host in nodes.NODES:
        
        # Go over all domains on the node 
        conn = connections[host]
        ids = conn.listDomainsID()
        for domain_id in ids:
            print '   Shutting down: %s' % (domain_id) 
            domain = conn.lookupByID(domain_id)
            domain.destroy()

 
def clone(source, target, count):
    # Create a new entry that describes the clone
    entry = QueueEntry(source, target, count)
    
    # Add the entry to the queue (thread safe) 
    reactor.callFromThread(queue.put, entry)
   
   
def main():
    # Establish libvirt connections and start reactor
    thr = start()
    
    # Stop everything
    shutdownall()
    
    # Schedule all clone entries
    index = 0
    for to_clone in clone_names:
        clone(to_clone[0], to_clone[1], index)
        index += 1
    
    # When to exit
    global exit_name
    exit_name = to_clone[-1]
    
    # Wait for exit
    print 'Waiting for clone process...'
    thr.join()
    print 'Exiting'
    

if __name__ == '__main__':
    main()
