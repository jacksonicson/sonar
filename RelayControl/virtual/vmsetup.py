from control import drones, hosts
from datetime import datetime
from lxml import etree
from rain import RainService, constants, ttypes
from relay import RelayService
from thrift import Thrift, Thrift
from thrift.protocol import TBinaryProtocol, TBinaryProtocol
from thrift.transport import TSocket, TTransport, TTwisted
from twisted.internet import defer, reactor
from twisted.internet.defer import inlineCallbacks
from twisted.internet.protocol import ClientCreator
import libvirt

DEFAULT_SETUP_IP = '192.168.110.246'
RELAY_PORT = 7900

conn = None

def update_done(ret, relay_conn):
    print 'Update executed'
    
    
    # Schedule next VM clone
    reactor.callLater(0, next_vm)


def done(ret):
    print 'Connection established'
    
    drone = drones.load_drone('setup_vm')
    
    # Do the setup process
    ret.launchNoWait(drone.data, drone.name).addCallback(update_done, ret)
        

def error(err, vm):
    # print 'ERRO %s' % (err)
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
    
    creator.addCallback(done)
    creator.addErrback(error, vm)
    


def clone(source, target):
    # Load VM
    domain = conn.lookupByName(source)
    pool = conn.storagePoolLookupByName("s0a0")
    volume = pool.storageVolLookupByName(source + ".img")

    # Reconfigure the volume     
    xml_vol_desc = volume.XMLDesc(0)
    
    xml_tree = etree.fromstring(xml_vol_desc)
    name = xml_tree.xpath('/volume/name')[0]
    name.text = target + '.img'
    
    key = xml_tree.xpath('/volume/key')[0]
    key.text = '/mnt/s0a0/' + target + '.img'
    
    path = xml_tree.xpath('/volume/target/path')[0]
    path.text = '/mnt/s0a0/' + target + '.img'
    
    xml_vol_desc = etree.tostring(xml_tree)
    #print xml_vol_desc
    
    # Create a new volume
    # new_volume = pool.createXMLFrom(xml_vol_desc, volume, 0)
    
    # Reconfigure the domain
    xml_domain_desc = domain.XMLDesc(0)
    
    xml_tree = etree.fromstring(xml_domain_desc)
    name = xml_tree.xpath('/domain/name')[0]
    name.text = target
    
    uuid = xml_tree.xpath('/domain/uuid')[0]
    uuid.getparent().remove(uuid)
    
    source = xml_tree.xpath('/domain/devices/disk/source')[0]
    source.set('file', '/mnt/s0a0/' + target + '.img')
    
    mac = xml_tree.xpath('/domain/devices/interface/mac')[0]
    mac.getparent().remove(mac)
    
    xml_domain_desc = etree.tostring(xml_tree)
    print xml_domain_desc
    
    # Create a new Domain
    # conn.defineXML(xml_domain_desc)
   
   
count = 0
def next_vm():
    global count
    count += 1
    
    if count > 1:
        print 'exiting...'
        conn.close()
        reactor.stop()  
        return
    
    clone('jacksch', 'test0')
    setup('test0')
    
       


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
