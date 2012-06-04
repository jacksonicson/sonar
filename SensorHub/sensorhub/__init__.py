from collector import CollectService, ManagementService, ttypes
from thrift import Thrift
from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport
import sched
import sys
import time





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
    
    list = client.getSensorLabels("cpu");
    print "Sensor labels"
    for i in list:
        print i

    sensors = client.getSensors("srv2")
    for sensor in sensors:
        print 'sensor found ' + sensor


    sensor_configurations = {}

        
    s = sched.scheduler(time.time, time.sleep)
    
    def print_time(sensor, sensorConfiguration): 
        print "From print_time", time.time()
        
        # Push dummy time series data to the collector
        ids = ttypes.Identifier();
        ids.timestamp = int(time.time())
        ids.sensor = sensor
        ids.hostname = "srv2" 
        
        value = ttypes.MetricReading();
        value.value = 100
        value.labels = []
        
        print "logging metric..."
        client2.logMetric(ids, value)
        
        s.enter(1, 1, print_time, (sensor, sensorConfiguration))
        
    
    
    # Download all the sensors
    for sensor in sensors: 
        sensorConfiguration = client.getBundledSensorConfiguration(sensor, "srv2") 
        print sensorConfiguration
        sensor_configurations[sensor] = sensorConfiguration;
        
        s.enter(1, 1, print_time, (sensor, sensorConfiguration))
    
    s.run()
    

if __name__ == '__main__':
    main(); 
