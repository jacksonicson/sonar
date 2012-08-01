from lxml import etree
import libvirt

def setup(vm):
    pass


def clone(conn, source, target):
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
    new_volume = pool.createXMLFrom(xml_vol_desc, volume, 0)
    
    # Reconfigure the domain
    xml_domain_desc = domain.XMLDesc(0)
    
    xml_tree = etree.fromstring(xml_domain_desc)
    name = xml_tree.xpath('/domain/name')[0]
    name.text = target
    
    source = xml_tree.xpath('/domain/devices/disk/source')[0]
    source.set('file', '/mnt/s0a0/' + target + '.img')
    
    mac = xml_tree.xpath('/domain/devices/interface/mac')[0]
    mac.getparent().remove(mac)
    
    xml_domain_desc = etree.tostring(xml_tree)
    print xml_domain_desc
    
    # Create a new Domain
    conn.createXML(xml_domain_desc, 0)
         


def main():
    print 'connecting'
    conn = libvirt.open("qemu+ssh://root@srv0/system")
    
    clone(conn, 'jacksch', 'test0')
    setup('test0')
    
    print 'exiting...'
    conn.close()


if __name__ == '__main__':
    main()
