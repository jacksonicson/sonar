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
DEFAULT_SETUP_IP = '192.168.110.246'
RELAY_PORT = 7900
###############################################

'''
All Domains (VMs) are setup on the srv0 system! This is the initialization system. If a Domain is moved 
to another system it's configuration has to be created on the target system. 
'''


conn = None

def update_done(ret, relay_conn):
    print 'Update executed'
    
    
    # Schedule next VM clone
    reactor.callLater(0, next_vm)


def done(ret, vm):
    print 'Connection established'
    
    try:
        config = open('drones/setup_vm/main_template.sh', 'r')
        data = config.readlines()
        data = ''.join(data)
        config.close()
        
        # print data
    
        templ = Template(data)
        d = dict(hostname=vm)
        templ = templ.substitute(d)
            
        config = open('drones/setup_vm/main.sh', 'w')
        config.writelines(templ)
        config.close()
    
        print templ
    except Exception, e:
        print e
        reactor.stop()
        return
   
    # Rebuild drones
    drones.main()
    
    drone = drones.load_drone('setup_vm')
    
    # Do the setup process
    ret.launchNoWait(drone.data, drone.name).addCallback(update_done, ret)
        

def error(err, vm):
    print 'Warn %s' % (err)
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
    


def clone(source, target):
    # Load VM
    domain = conn.lookupByName(source)
    pool = conn.storagePoolLookupByName("s0a0")
    volume = pool.storageVolLookupByName(source + ".qcow")

    # Reconfigure the volume     
    xml_vol_desc = volume.XMLDesc(0)
    
    xml_tree = etree.fromstring(xml_vol_desc)
    name = xml_tree.xpath('/volume/name')[0]
    name.text = target + '.qcow'
    
    key = xml_tree.xpath('/volume/key')[0]
    key.text = '/mnt/s0a0/' + target + '.qcow'
    
    path = xml_tree.xpath('/volume/target/path')[0]
    path.text = '/mnt/s0a0/' + target + '.qcow'
    
    xml_vol_desc = etree.tostring(xml_tree)
    #print xml_vol_desc
    
    # Create a new volume
    print 'Cloning volume...'
    new_volume = pool.createXMLFrom(xml_vol_desc, volume, 0)
    
    # Reconfigure the domain
    xml_domain_desc = domain.XMLDesc(0)
    
    xml_tree = etree.fromstring(xml_domain_desc)
    name = xml_tree.xpath('/domain/name')[0]
    name.text = target
    
    uuid = xml_tree.xpath('/domain/uuid')[0]
    uuid.getparent().remove(uuid)
    
    source = xml_tree.xpath('/domain/devices/disk/source')[0]
    source.set('file', '/mnt/s0a0/' + target + '.qcow')
    
    mac = xml_tree.xpath('/domain/devices/interface/mac')[0]
    mac.getparent().remove(mac)
    
    xml_domain_desc = etree.tostring(xml_tree)
    print xml_domain_desc
    
    # Create a new Domain
    print 'Creating Domain...'
    new_domain = conn.defineXML(xml_domain_desc)
    #new_domain = conn.lookupByName(target)
    
    # Launch it
    print 'Starting Domain...'
    new_domain.create()
   
   
count = 0
clone_names = [('playground', 'glassfish0'),
               ('playground', 'glassfish1'),
               ('playground', 'glassfish2'),
               ('playground', 'glassfish3'),
               ('playground', 'glassfish4'),
               ('playground', 'glassfish5'),
               ('playdb', 'mysql0'),
               ('playdb', 'mysql1'),
               ('playdb', 'mysql2'),
               ('playdb', 'mysql3'),
               ('playdb', 'mysql4'),
               ('playdb', 'mysql5'), ]

def next_vm():   
    global count
    
    if count >= len(clone_names):
        print 'exiting...'
        conn.close()
        reactor.stop()  
        return
    
    job = clone_names[count]
    print 'Launching job %s -> %s' % job
    count += 1
    
    clone(job[0], job[1])
    setup(job[1])


def main():
    # Create drones
    drones.main()
    
    print 'connecting'
    global conn
    conn = libvirt.open("qemu+ssh://root@srv0/system")

    reactor.callLater(0, next_vm)
    reactor.run()
    

if __name__ == '__main__':
    main()
