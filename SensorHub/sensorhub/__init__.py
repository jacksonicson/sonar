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

HOSTNAME = 'srv2' # gethostname(); 
SENSORHUB = 'sensorhub'

def registerSensorHub(managementClient, hostname):
    # Ensure that the hostname is registered
    print 'Adding host: %s' % (hostname)
    managementClient.addHost(hostname); 
    
    # Setup the self monitoring SENSORHUB sensor
    sensor = managementClient.fetchSensor(SENSORHUB)
    if len(sensor) == 0: 
        print 'Deploying sensor: %s' % (SENSORHUB)
        managementClient.deploySensor(SENSORHUB, '  ')
        
    # Enable sensor for hostname
    print 'Enabling sensor: %s for host: %s' % (SENSORHUB, hostname)
    managementClient.setSensor(hostname, SENSORHUB, True)
        

def main():
    # Make socket
    transport = TSocket.TSocket('localhost', 7931)
    transport2 = TSocket.TSocket("localhost", 7921)
    
    # Buffering is critical. Raw sockets are very slow
    transport = TTransport.TBufferedTransport(transport)
    transport2 = TTransport.TBufferedTransport(transport2) 
    
    # Wrap in a protocol
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    protocol2 = TBinaryProtocol.TBinaryProtocol(transport2); 
    
    client = ManagementService.Client(protocol);
    client2 = CollectService.Client(protocol2);  
    
    transport.open();
    transport2.open(); 
    
    registerSensorHub(client, HOSTNAME); 
    
    sensors = client.getSensors(HOSTNAME)
    for sensor in sensors:
        print 'sensor found ' + sensor

    sensor_configurations = {}
        
    s = sched.scheduler(time.time, time.sleep)
    
    def print_time(sensor, bundledConfiguration): 
        print "From print_time", time.time()
        
        # Push dummy time series data to the collector
        ids = ttypes.Identifier();
        ids.timestamp = int(time.time())
        ids.sensor = sensor
        ids.hostname = HOSTNAME 
        
        value = ttypes.MetricReading();
        
        
        value.value = random.randint(1, 100)
        value.labels = []
        
        print "logging metric..."
        client2.logMetric(ids, value)
        
        print "Sensor configuration interval: %i" % (bundledConfiguration.configuration.interval) 
        s.enter(bundledConfiguration.configuration.interval, 1, print_time, (sensor, bundledConfiguration))
        
    
    
    # Download all the sensors
    for sensor in sensors:
        # Download sensor package
        
        if os.path.exists(sensor + ".zip"):
            print 'removing sensor' 
            os.remove(sensor + ".zip")
            
        print 'downloading sensor ...'
        data = client.fetchSensor(sensor)
        z = open(sensor + ".zip", "wb")
        z.write(data)
        z.close()
        print 'sensor download complete'
        
        print 'decompressing sensor ...'
        decompress_sensor(sensor); 
        print 'sensor decompression completed'
        
        # Configure and schedule sensor 
        bundledConfiguration = client.getBundledSensorConfiguration(sensor, HOSTNAME) 
        print bundledConfiguration
        sensor_configurations[sensor] = bundledConfiguration;
        
        # s.enter(bundledConfiguration.configuration.interval, 1, print_time, (sensor, bundledConfiguration))
        
    s.enter(5, 1, self_monitoring, (client2, s))
    s.run()


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
