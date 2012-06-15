from constants import SENSORHUB

def downloadSensor(sensor):
    # Get the MD5 value of the binary
    testMd5 = managementClient.sensorHash(sensor)
    
    # Check if MD5 changed since the last fetch
    if sensorConfiguration.has_key(sensor):
        md5 = sensorConfiguration[sensor].md5
        if md5 == testMd5:
            return md5
            
    # Download sensor package
    if os.path.exists(sensor + ".zip"):
        os.remove(sensor + ".zip")
        
    # Download sensor
    data = managementClient.fetchSensor(sensor)
    z = open(sensor + ".zip", "wb")
    z.write(data)
    z.close()
    
    # Decompress sensor package            
    package.decompress_sensor(sensor);
    return testMd5

def registerSensorHub(managementClient, hostname):
    # Ensure that the hostname is registered
    print 'Adding host: %s' % (hostname)
    managementClient.addHost(hostname); 
    
    # Setup the self-monitoring SENSORHUB sensor
    sensor = managementClient.fetchSensor(SENSORHUB)
    if len(sensor) == 0: 
        print 'Deploying sensor: %s' % (SENSORHUB)
        managementClient.deploySensor(SENSORHUB, '  ')
        
    # Enable sensor for hostname
    print 'Enabling sensor: %s for host: %s' % (SENSORHUB, hostname)
    managementClient.setSensor(hostname, SENSORHUB, True)
        