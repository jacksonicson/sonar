import drones

drones.prepare_drone('glassfish_configure', 'domain.xml', mysql_server='mysql0')
drones.create_drone('glassfish_configure')
