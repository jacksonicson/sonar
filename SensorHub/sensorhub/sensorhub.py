from collector import CollectService, ManagementService, ttypes
from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport
import sched
import time
import monitor
import os
import os
import zipfile
import shutil
from constants import SENSOR_DIR

import thread 
from select import select
from subprocess import Popen, PIPE
from constants import SENSOR_DIR, HOSTNAME, SENSORHUB

# difference thread and threading
from threading import Thread

class Sensor(object):
    
    def __init__(self, loggingClient):
        self.loggingClient = loggingClient
    
    def data(self, line):
        ids = ttypes.Identifier();
        ids.timestamp = int(time.time())
        ids.sensor = self.name
        ids.hostname = HOSTNAME
        
        value = ttypes.MetricReading();
        value.value = long(float(line))
        value.labels = []
            
        self.loggingClient.logMetric(ids, value)
            
        print "value %f for sensor %s" % (float(line), self.name)
        
    
    def validate(self):
        exists = False
        target = SENSOR_DIR + self.name + "/main"
        exists |= os.path.exists(target)
        
        target = SENSOR_DIR + self.name + "/main.exe"
        exists |= os.path.exists(target)
        
        target = SENSOR_DIR + self.name + "/main.py"
        exists |= os.path.exists(target)
        
        return exists

    
    def decompress(self):
        zf = zipfile.ZipFile(sensor + ".zip")
        
        target = SENSOR_DIR + sensor + "/"
        
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


class ProcessLoader(object):
    def execute(self, sensor):
        # create a new process 
        try:
            path = os.path.join(SENSOR_DIR, sensor.name + '/main.py')
            process = Popen(['python', path], stdout=PIPE, bufsize=1, universal_newlines=True)
            return process
        except Exception as e:
            print 'error starting process %s' % (e)
            return None
    
    def kill(self, process):
        try:
            process.kill()
        except Exception as e:
            print 'error while killing process %s' % (e)
            
   
class ContinuouseWatcher(Thread, ProcessLoader):
    
    SLEEP = 0.5
    
    def __init__(self, lock):
        # thread locking object
        self.lock = lock
        
        # list of sensors assigned to this watcher
        self.sensors = []
        
        # list of processes started by this watcher 
        self.processes = []

    
    def addSensor(self, sensor):
        process = super(ProcessLoader, self).execute(sensor)
        if process != None:
            self.lock.acquire()
            self.sensors.append(process)
            self.processes.append(process)
            self.lock.release()


    def shutdownSensor(self, sensor):
        self.lock.acquire()
        
        for i in range(0, len(self.sensors)):
            if self.sensors[i] == sensor:
                # remove sensor
                del self.sensors[i]
                
                # terminate and remove process
                super(ProcessLoader, self).kill(self.processes[i])
                del self.processes[i]
        
        self.lock.release()
        
        
    def run(self):
        while True:
            # Update streams list
            streams = []
            self.lock.acquire()
            for process in self.processes:
                streams.append(process.stdout)
            self.lock.release()
            
            if len(streams) == 0:
                time.sleep(ContinuouseWatcher.SLEEP)
                continue
            
            # Wait for data and pick the stdout list
            data = select(streams, [], [], ContinuouseWatcher.SLEEP)[0] 
            
            self.lock.acquire()
            for i in range(0, len(data)):
                sensor = self.sensors[i]
                
                line = data[i]
                line = line.readline()
                line = line.strip().rstrip()
                
                sensor.data(line)
                
            self.lock.release()
    
    

def configureSensor(sensor):
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
