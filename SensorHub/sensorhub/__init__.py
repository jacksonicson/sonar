from collector import CollectService, ManagementService, ttypes
from thrift import Thrift
from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport
import sched
import sys
import time
from socket import gethostname;
import zlib
import zipfile
import os
import random;
import shutil 

HOSTNAME = gethostname(); 
SENSORHUB = 'sensorhub'

sensorScheduler = None
sensorConfiguration = {}

managementClient = None
loggingClient = None

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
        

class SensorHandler:
    
    def __init__(self, sensor, logClient):
        self.sensor = sensor
        self.logClient = logClient
        
    def execute(self, sensorScheduler):
        self.runBinary()
        
        global sensorConfiguration
        if sensorConfiguration.has_key(self.sensor):
            sensorScheduler.enter(self.configuration.configuration.interval, 0, self.execute, [sensorScheduler])
        else:
            print 'Stopping sensor: %s' % (self.sensor) 
        
    def runBinary(self):
        print "running %s" % (self.sensor)
        
        
        pass
    

def updateSensors():
    print 'Updating sensors...'
    
    global sensorConfiguration
    global sensorScheduler
    
    # Download all the sensors
    sensors = managementClient.getSensors(HOSTNAME)

    # Remove old sensors
    for test in sensorConfiguration.keys():
        if test not in sensors:
            sensorConfiguration.pop(test)
    
    # Update configuration for the remaining sensors
    for sensor in sensors:
        print 'sensor found ' + sensor
        
        # Do not enable sensorhub
        if sensor == SENSORHUB:
            continue
        
        # Check MD5
        testMd5 = managementClient.sensorHash(sensor)
        refetch = True
        if sensorConfiguration.has_key(sensor):
            md5 = sensorConfiguration[sensor].md5
            if md5 == testMd5:
                print 'skipping sensor download for %s' % (sensor)
                refetch = False
                
        if refetch:
            # Download sensor package
            if os.path.exists(sensor + ".zip"):
                print 'removing sensor %s ' % (sensor) 
                os.remove(sensor + ".zip")
                
            print 'downloading sensor %s ...' % (sensor)
            data = managementClient.fetchSensor(sensor)
            z = open(sensor + ".zip", "wb")
            z.write(data)
            z.close()
            print 'download complete'
            
            print 'decompressing sensor ...'
            # decompress_sensor(sensor);     
            print 'decompression completed'
        
        
        # Configure and schedule sensor
        if not sensorConfiguration.has_key(sensor):
            sensorConfiguration[sensor] = SensorHandler(sensor, loggingClient)
            sensorConfiguration[sensor].configuration = managementClient.getBundledSensorConfiguration(sensor, HOSTNAME)
            sensorConfiguration[sensor].md5 = testMd5
            
            print 'enabling sensor %s with interval %i' % (sensor, sensorConfiguration[sensor].configuration.configuration.interval)
            sensorScheduler.enter(sensorConfiguration[sensor].configuration.configuration.interval, 0, sensorConfiguration[sensor].execute, [sensorScheduler])
        else:
            print 'update'
            sensorConfiguration[sensor].configuration = managementClient.getBundledSensorConfiguration(sensor, HOSTNAME)
            sensorConfiguration[sensor].md5 = testMd5
  
  
def regularUpdateWrapper():
    global sensorScheduler
    updateSensors()
    sensorScheduler.enter(7, 0, regularUpdateWrapper, [])
        

def main():
    print 'Hostname of this machine: %s' % (HOSTNAME)
    
    # Make socket
    trasportManagement = TSocket.TSocket('localhost', 7931)
    transportLogging = TSocket.TSocket("localhost", 7921)
    
    # Buffering is critical. Raw sockets are very slow
    trasportManagement = TTransport.TBufferedTransport(trasportManagement)
    transportLogging = TTransport.TBufferedTransport(transportLogging) 
    
    # Setup the clients
    global managementClient
    managementClient = ManagementService.Client(TBinaryProtocol.TBinaryProtocol(trasportManagement));
    
    global loggingClient
    loggingClient = CollectService.Client(TBinaryProtocol.TBinaryProtocol(transportLogging));  
    
    # Open the transports
    trasportManagement.open();
    transportLogging.open(); 
    
    # Register hostname and self-monitoring sensor
    registerSensorHub(managementClient, HOSTNAME); 

    # Setup sensorScheduler
    global sensorScheduler;
    sensorScheduler = sched.scheduler(time.time, time.sleep)
    
    # Fetch and configure sensors
    sensorScheduler.enter(5, 1, self_monitoring, (loggingClient, sensorScheduler))
    regularUpdateWrapper()
    
    # Run sensorScheduler
    sensorScheduler.run()


def self_monitoring(client, s):
    ids = ttypes.Identifier();
    ids.timestamp = int(time.time())
    ids.sensor = 'sensorhub'
    ids.hostname = HOSTNAME 

    value = ttypes.MetricReading();
    value.value = 1
    value.labels = []
    
    client.logMetric(ids, value)
    
    ids.timestamp = ids.timestamp + 1
    value.value = 0
    client.logMetric(ids, value)
    
    s.enter(5, 1, self_monitoring, (client, s))
    


def decompress_sensor(sensor):
    zf = zipfile.ZipFile(sensor + ".zip")
    
    target = '../sensors/' + sensor + "/"
    
    if os.path.exists(target):
        print 'removing sensor directory: ' + target
        shutil.rmtree(target, True)
    
    try:
        os.makedirs(target)
    except:
        pass
    
    for info in zf.infolist():
        print info.filename

        if info.filename.endswith('/'):
            try:
                print 'creating directory ' + info.filename
                os.makedirs(target + info.filename)
            except:
                print 'fail'
            continue
        
        cf = zf.read(info.filename)
        
        f = open(target + info.filename, "wb")
        f.write(cf)
        f.close()
        
    zf.close()


if __name__ == '__main__':
    main()
