from collector import CollectService, ManagementService, ttypes
from constants import SENSOR_DIR, SENSOR_DIR, HOSTNAME, SENSORHUB
from select import select
from sensorhub.management import registerSensorHub
from subprocess import Popen, PIPE
from threading import Thread
from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport
import monitor
import os
import os
import sched
import shutil
import thread
import time
import zipfile

class Sensor(object):

    CONTINUOUSE = 0
    DISCRETE = 1 
    
    def __init__(self, name, loggingClient, managementClient):
        self.loggingClient = loggingClient
        self.managementClient = managementClient
        self.name = name
    
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
        
        
    def __download(self):
        # Get the MD5 value of the binary
        testMd5 = self.managementClient.sensorHash(self.name)
        
        # Check if MD5 changed since the last fetch
        if self.sensorConfiguration.has_key(self.name):
            if self.md5 == testMd5:
                return self.md5
                
        # Download sensor package
        if os.path.exists(self.name + ".zip"):
            os.remove(self.name + ".zip")
            
        # Download sensor
        data = self.managementClient.fetchSensor(self.name)
        z = open(self.sensor + ".zip", "wb")
        z.write(data)
        z.close()
        
        # Decompress sensor package            
        self.__decompress()
        
        return testMd5
        
        
    def configure(self):
        # Do not enable self-monitoring sensor
        if self.name == SENSORHUB:
            return
        
        # Only accept sensors with binaries
        if not self.managementClient.hasBinary(self.name):
            return

        # Get MD5 value
        self.md5 = self.__download()
    
    
    def validate(self):
        exists = False
        target = SENSOR_DIR + self.name + "/main"
        exists |= os.path.exists(target)
        
        target = SENSOR_DIR + self.name + "/main.exe"
        exists |= os.path.exists(target)
        
        target = SENSOR_DIR + self.name + "/main.py"
        exists |= os.path.exists(target)
        
        return exists

    
    def __decompress(self):
        zf = zipfile.ZipFile(self.name + ".zip")
        
        target = os.path.join(SENSOR_DIR, self.name)
        
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
            
   
class DiscreteWatcher(ProcessLoader):
    
    def __init__(self, lock, scheduler):
        self.lock = lock
        self.scheduler = scheduler
        
        self.sensors = []
        
    
    def addSensor(self, sensor):
        self.sensors.append(sensor)
        
   
class ContinuouseWatcher(Thread, ProcessLoader):
    
    SLEEP = 0.5
    
    def __init__(self, lock):
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
    
    

class SensorHub(object):
    def __init(self, lock, managementClient, loggingClient, scheduler):
        self.lock = lock
        self.managementClient = managementClient
        self.loggingClient = loggingClient
        self.scheduler = scheduler
        
        # Map of all sensors (key = sensor name, value = instance of Sensor)
        self.sensors = {}
        
        # Create watchers
        self.continuouseWatcher = ContinuouseWatcher(self.lock)
        self.discreteWatcher = DiscreteWatcher(self.lock, self.scheduler)
        
        # Watch
        self.__regularUpdateWrapper()   
        

    def __regularUpdateWrapper(self):
        self.lock.acquire()
        self.__updateSensors()
        self.lock.release()
    
        self.scheduler.enter(5, 0, self.__updateSensors, [])
     
     
    def __updateSensors(self):
        # Download all the sensors
        sensors = self.managementClient.getSensors(HOSTNAME)
    
        # Remove sensors
        sensorsMap = dict([(k, None) for k in sensors])
        for test in self.sensors.keys():
            if test not in sensorsMap:
                self.__disableSensor(test)
                
        # Get all new sensors
        toAdd = [item for item in sensors if item not in self.sensor]
        
        # Update configuration for the remaining sensors
        for sensor in toAdd:
            self.__setupSensor(sensor)
   
   
    def __setupSensor(self, sensorName):
        sensor = Sensor(sensorName, self.loggingClient, self.managementClient)
        self.sensors.append(sensor)
        
        if sensor.type() == Sensor.CONTINUOUSE:
            self.continuouseWatcher.addSensor(sensor)
        elif sensor.type() == Sensor.DISCRETE:
            self.discreteWatcher.addSensor(sensor)

    def __disableSensor(self, sensorName):
        print 'disabling sensor %s' % (sensorName)
        self.sensors.pop(sensorName)
    

    def join(self):
        self.continuouseWatcher.join()
        self.discreteWatcher.join()


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
    managementClient = ManagementService.Client(TBinaryProtocol.TBinaryProtocol(trasportManagement));
    loggingClient = CollectService.Client(TBinaryProtocol.TBinaryProtocol(transportLogging));  
    
    # Open the transports
    trasportManagement.open();
    transportLogging.open(); 
    
    # Setup thread lock
    lock = thread.allocate_lock()
    
    # Setup sensorScheduler
    sensorScheduler = sched.scheduler(time.time, time.sleep)
    
    # Setup sensorHub
    sensorHub = SensorHub(lock, managementClient, loggingClient, sensorScheduler)
    
    # Scheduler self monitoring
    sensorScheduler.enter(5, 1, self_monitoring, (loggingClient, sensorScheduler))
    
    # Wait for scheduler and continuouse thread
    sensorScheduler.run()
    sensorHub.join()


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

# jump into the main method
if __name__ == '__main__':
    main()
