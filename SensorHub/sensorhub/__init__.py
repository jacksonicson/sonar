from collector import CollectService, ManagementService, ttypes
from thrift import Thrift
from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport
import sched
import sys
import time
from socket import gethostname;

import random; 

HOSTNAME = 'srv2' # gethostname(); 





def main():
    print "test"
    
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
        
        s.enter(bundledConfiguration.configuration.interval, 1, print_time, (sensor, bundledConfiguration))
    
    s.run()

import zlib
import zipfile
import os
def decompress_sensor(sensor):
    zf = zipfile.ZipFile(sensor + ".zip")
    
    for info in zf.infolist():
        print info.filename
        
        target = '../sensors/' + sensor + "/"
        try:
            os.makedirs(target)
        except:
            pass


        if info.filename.endswith('/'):
            try:
                print 'creating directory ' + info.filename
                os.makedirs(target + info.filename)
            except:
                pass
            continue
        
        cf = zf.read(info.filename)
        
        f = open(target + info.filename, "wb")
        f.write(cf)
        f.close()
        
    zf.close()

def testzip():
    
    f = open("../cpu.zip", "rb")
    ba = bytearray()
    
    byte = f.read(1)
    while byte:
        ba.extend(byte)
        byte = f.read(1)
        
        
    f.close()


    print ba       
    
    
    
    
#    for filename in [ 'README.txt', 'notthere.txt' ]:
#    try:
#        data = zf.read(filename)
#    except KeyError:
#        print 'ERROR: Did not find %s in zip file' % filename
#    else:
#        print filename, ':'
#        print repr(data)
#    print
#    
#    print ba    
    
    
    pass

if __name__ == '__main__':
    main()
   # testzip() 
