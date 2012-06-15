from collector import CollectService, ManagementService, ttypes
from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport
import sched
import time
from socket import gethostname;

import os

import subprocess
import thread 
from select import select
from subprocess import Popen, PIPE
import package

# Constants
HOSTNAME = gethostname()
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
        
        print "Thread: %i" % (thread.get_ident())
        
        target = ""
        if os.path.exists(SENSOR_DIR + self.sensor + "/main"):
            target = SENSOR_DIR + self.sensor + "/main"
        elif os.path.exists(SENSOR_DIR + self.sensor + "/main.exe"):
            target = SENSOR_DIR + self.sensor + "/main.exe"
        elif os.path.exists(SENSOR_DIR + self.sensor + "/main.py"):
            target = "python " + SENSOR_DIR + self.sensor + "/main.py"
            
        print "Running %s " % (target)
            
        p = subprocess.Popen(target + " >&2", stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout, stderr = p.communicate()
        lines = stdout.decode('ascii').splitlines()
        count = 0
        
        print "error %s" % (stderr)
        
        for line in lines:
            
            print "line: %s" % (line)
            
            ids = ttypes.Identifier();
            ids.timestamp = int(time.time() + count)
            ids.sensor = self.sensor
            ids.hostname = HOSTNAME

            count += 1
            
            value = ttypes.MetricReading();
            value.value = long(float(line))
            value.labels = []
            
            print "value: %i" % (value.value)
            
            self.logClient.logMetric(ids, value)
        
        pass
    


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
    decompress_sensor(sensor);
    return testMd5
    
    
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
        sensorConfiguration[sensor] = SensorHandler(sensor, loggingClient)
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
    sensorScheduler.enter(5, 1, self_monitoring, (loggingClient, sensorScheduler))
    regularUpdateWrapper(lock)
    
    # Run sensorScheduler
    sensorScheduler.run()





if __name__ == '__main__':
    main()
