from collector import CollectService, ManagementService, ttypes
from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport
import sched
import time
import monitor
import os

import thread 
from select import select
from subprocess import Popen, PIPE
from constants import SENSOR_DIR
import package

class PipeAdapter(object):
    
    def __init__(self, lock):
        self.lock = lock 


class SensorHub(object):
    
    activeSensors = {}
    
    def __init__(self):
        pass
    
def continuousThread(lock, loggingClient):
    print 'Continuous thread launched'
    global sensorConfiguration
    
    while True:
        waitList = []
        sensorList = []
        
        lock.acquire()
        for sensor in sensorConfiguration.keys():
            if sensorConfiguration[sensor].continuous is True:
                if hasattr(sensorConfiguration[sensor], 'process') == False:
                    path = SENSOR_DIR + sensorConfiguration[sensor].sensor + "/main.py"
                    print 'launching path %s' % (path)
                    process = Popen(['python', path], stdout=PIPE, bufsize=1, universal_newlines=True)
                    print "Process launched"
                    
                    sensorConfiguration[sensor].process = process
                    waitList.append(process.stdout)
                    sensorList.append(sensorConfiguration[sensor])
                else:
                    waitList.append(sensorConfiguration[sensor].process.stdout)
                    sensorList.append(sensorConfiguration[sensor])
        
        lock.release()
        
        if len(waitList) == 0:
            time.sleep(1)
            continue
        
        
        # Transfer data each secondd
        # The pipes have to hold the data of one second!
        ll = select(waitList, [], [], 1)[0] # get only the read list
        
        lock.acquire()
        
        for i in range(0, len(ll)):
            ll = ll[i]
            sensor = sensorList[i]
            try:
                line = ll.readline()
                line = line.strip()
                line = line.rstrip()
                
                # value = float(line)
                
                ids = ttypes.Identifier();
                ids.timestamp = int(time.time())
                ids.sensor = sensor.sensor
                ids.hostname = HOSTNAME
    
                value = ttypes.MetricReading();
                value.value = long(float(line))
                value.labels = []
                
                loggingClient.logMetric(ids, value)
                
                print "value %f for sensor %s" % (float(line), sensor.sensor)
                
                
            except Exception as e:
                print 'error %s' % e
        
        lock.release()
        
        pass
    

def configureSensor(sensor):
    global sensorConfiguration
    global sensorScheduler
    
    # Do not enable self-monitoring sensor
    if sensor == SENSORHUB:
        return
    
    # Only accept sensors with binaries
    if not managementClient.hasBinary(sensor):
        return
    
    # Download sensor
    md5 = downloadSensor(sensor)
    
    # Check if we see this sensor the first time
    if not sensorConfiguration.has_key(sensor):
        # Configure and schedule sensor
        sensorConfiguration[sensor] = Sensor(sensor, loggingClient)
        sensorConfiguration[sensor].configuration = managementClient.getBundledSensorConfiguration(sensor, HOSTNAME)
        sensorConfiguration[sensor].md5 = md5
        
        print 'enabling sensor %s' % (sensor)
        if sensorConfiguration[sensor].configuration.configuration.interval == 0:
            sensorConfiguration[sensor].continuous = True
        else:
            sensorConfiguration[sensor].continuous = False
            sensorScheduler.enter(sensorConfiguration[sensor].configuration.configuration.interval, 0, sensorConfiguration[sensor].execute, [sensorScheduler])
    else:
        # Updating sensor
        sensorConfiguration[sensor].configuration = managementClient.getBundledSensorConfiguration(sensor, HOSTNAME)
        sensorConfiguration[sensor].md5 = md5


def disableSensor(sensor):
    print 'disabling sensor %s' % (sensor)

    if sensorConfiguration[sensor].continuous == True:
        if hasattr(sensorConfiguration[sensor], 'process'):
            print 'terminating process %s ' % (sensor)
            sensorConfiguration[sensor].process.kill()
    
    sensorConfiguration.pop(sensor)
    

def updateSensors():
    global sensorConfiguration
    
    # Download all the sensors
    sensors = managementClient.getSensors(HOSTNAME)

    # Remove sensors
    sensorsMap = dict([(k, None) for k in sensors])
    for test in sensorConfiguration.keys():
        if test not in sensorsMap:
            disableSensor(test)
            
    # Get all new sensors
    toAdd = [item for item in sensors if item not in sensorConfiguration]
    
    # Update configuration for the remaining sensors
    for sensor in toAdd:
        configureSensor(sensor)

  
def regularUpdateWrapper(lock):
    global sensorScheduler
    
    lock.acquire()
    updateSensors()
    lock.release()
    
    sensorScheduler.enter(7, 0, regularUpdateWrapper, [lock])

def main():
    print 'Hostname of this machine: %s' % (HOSTNAME)
    print 'Main thread id: %i' % (thread.get_ident())
    
    # Make socket
    trasportManagement = TSocket.TSocket('169.254.102.106', 7931)
    transportLogging = TSocket.TSocket("169.254.102.106", 7921)
    
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

    # Setup thread
    lock = thread.allocate_lock()
    thread.start_new_thread(continuousThread, (lock, loggingClient))

    # Setup sensorScheduler
    global sensorScheduler;
    sensorScheduler = sched.scheduler(time.time, time.sleep)
    
    # Fetch and configure sensors
    sensorScheduler.enter(5, 1, monitor.self_monitoring, (loggingClient, sensorScheduler))
    regularUpdateWrapper(lock)
    
    # Run sensorScheduler
    sensorScheduler.run()





if __name__ == '__main__':
    main()
