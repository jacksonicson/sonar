from collector import CollectService, ManagementService, ttypes
from constants import SENSOR_DIR, SENSOR_DIR, HOSTNAME, SENSORHUB
from select import select
from subprocess import Popen, PIPE
from threading import Thread
from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport
import os
import os
import sched
import shutil
import string
import thread
import time
import zipfile

VALID_MAINS = ('main', 'main.exe', 'main.py', 'main.sh')

class Sensor(object):

    CONTINUOUSE = 0
    DISCRETE = 1 
    
    def __init__(self, name, loggingClient, managementClient):
        self.loggingClient = loggingClient
        self.managementClient = managementClient
        self.name = name
        self.md5 = None
    
    def receive(self, line):
        # parsing line
        floatValue = None
        try:
            floatValue = long(float(line))
        except ValueError as e:
            print 'could not parse line %s' % (line)
            return
        
        
        ids = ttypes.Identifier();
        ids.timestamp = int(time.time())
        ids.sensor = self.name
        ids.hostname = HOSTNAME
        
        value = ttypes.MetricReading();
        value.value = floatValue
        value.labels = []
            
        self.loggingClient.logMetric(ids, value)
            
        print "value %f for sensor %s" % (float(line), self.name)
       
    def sensorType(self):
        return Sensor.DISCRETE
        
    def __download(self):
        # Get the MD5 value of the binary
        testMd5 = self.managementClient.sensorHash(self.name)
        
        # Check if MD5 changed since the last fetch
        if self.md5 == testMd5:
            return self.md5
                
        # Download sensor package
        if os.path.exists(self.name + ".zip"):
            os.remove(self.name + ".zip")
            
        # Download sensor
        data = self.managementClient.fetchSensor(self.name)
        z = open(self.name + ".zip", "wb")
        z.write(data)
        z.close()
        
        # Decompress sensor package            
        self.__decompress()
        
        return testMd5
        
        
    def configure(self):
        # Do not enable self-monitoring sensor
        if self.name == SENSORHUB:
            return False
        
        # Only accept sensors with binaries
        if not self.managementClient.hasBinary(self.name):
            return False

        # Download settings
        bundledConfiguration = self.managementClient.getBundledSensorConfiguration(HOSTNAME, self.name)
        self.settings = bundledConfiguration.configuration
        self.labels = bundledConfiguration.labels
        
        # Just for safety - this should never match because inactive sensors are
        # handled by the synchronization process
        if bundledConfiguration.active == False:
            return False

        # Get MD5 value
        self.md5 = self.__download()
        return True
    
    
    def validate(self):
        exists = False
        
        for main in VALID_MAINS:
            target = os.path.join(SENSOR_DIR, self.name, main)
            exists |= os.path.exists(target)
        
        return exists

    
    def __decompress(self):
        zf = zipfile.ZipFile(self.name + ".zip")
        
        target = os.path.join(SENSOR_DIR, self.name)
        
        if os.path.exists(target):
            shutil.rmtree(target, True)
        
        try:
            os.makedirs(target)
        except:
            pass
        
        for info in zf.infolist():
            print info.filename
    
            if info.filename.endswith('/'):
                try:
                    os.makedirs(target + info.filename)
                except Exception as e:
                    print 'error while decompressing files %s' % (e)
                continue
            
            cf = zf.read(info.filename)
            f = open(os.path.join(target, info.filename), "wb")
            f.write(cf)
            f.close()
            
        zf.close()


class ProcessLoader(object):
    def newProcess(self, sensor):
        # determine the executable
        mainFile = None
        for main in VALID_MAINS:
            target = os.path.join(SENSOR_DIR, self.name, main)
            if os.path.exists(target):
                mainFile = main
                break
            
        # break if there is no main file
        if mainFile == None:
            print 'missing main file for sensor %s' % (sensor.name)
            return
        
        # determine the executable (python, ..)
        executable = None
        try:    
            index = string.rindex(mainFile, '.')
            ending = string[index + 1:]
            if ending == 'py':
                executable = 'python'
            elif ending == 'sh':
                executable = None
            elif ending == 'exe':
                executable = None
        except ValueError:
            executable = None
        
        # create a new process 
        try:
            path = os.path.join(SENSOR_DIR, sensor.name + '/main.py')
            
            # configure executable and main file
            if executable is None:
                executable = [path,]
            else:
                executable = [executable, path]
            
            process = Popen(executable, stdout=PIPE, bufsize=1, universal_newlines=True)
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
    
    def __init__(self, scheduler):
        self.scheduler = scheduler
        self.sensors = []

    
    def addSensor(self, sensor):
        self.sensors.append(sensor)
        self.__callbackHandler(sensor)

    
    def shutdownSensor(self, sensor):
        self.sensors.remove(sensor)

        
    def __callbackHandler(self, sensor):
        # Scheduler triggered an invalidated sensor
        if sensor in self.sensors == False:
            return
        
        # Start a new process for each sensor call
        process = self.newProcess(sensor)
        if process != None:
            # get the stdout from the process
            line = process.communicate()[0]
            sensor.receive(line)
        
        self.scheduler.enter(sensor.settings.interval, 0, self.__callbackHandler, [sensor])
    
        
   
class ContinuouseWatcher(Thread, ProcessLoader):
    
    SLEEP = 0.5
    
    def __init__(self):
        super(ContinuouseWatcher, self).__init__()
        
        self.lock = thread.allocate_lock()
        
        # list of sensors assigned to this watcher
        self.sensors = []
        
        # list of processes started by this watcher 
        self.processes = []
        
        # Start the thread
        self.start()

    
    def addSensor(self, sensor):
        print 'Continuouse watcher adding sensor: %s' % (sensor)
        
        process = self.newProcess(sensor)
        if process != None:
            self.lock.acquire()
            self.sensors.append(sensor)
            self.processes.append(process)
            self.lock.release()


    def shutdownSensor(self, sensor):
        self.lock.acquire()
        
        for i in range(0, len(self.sensors)):
            if self.sensors[i] == sensor:
                # remove sensor
                del self.sensors[i]
                
                print 'terminating process'
                # terminate and remove process
                super(ContinuouseWatcher, self).kill(self.processes[i])
                del self.processes[i]
        
        self.lock.release()
        
        
    def run(self):
        while True:
            # Update streams list
            streams = []
            sensors = []
            
            self.lock.acquire()
            for i in range(0, len(self.processes)):
                streams.append(self.processes[i].stdout)
                sensors.append(self.sensors[i])
            self.lock.release()
        
            if len(streams) == 0:
                time.sleep(ContinuouseWatcher.SLEEP)
                continue
            
            # Wait for receive and pick the stdout list
            data = select(streams, [], [], ContinuouseWatcher.SLEEP)[0] 
            
            self.lock.acquire()
            for i in range(0, len(data)):
                sensor = sensors[i]
                
                line = data[i]
                line = line.readline()
                line = line.strip().rstrip()
                
                sensor.receive(line)
            self.lock.release()
    
    

class SensorHub(object):
    def __init__(self, lock, managementClient, loggingClient, scheduler):
        self.lock = lock
        self.managementClient = managementClient
        self.loggingClient = loggingClient
        self.scheduler = scheduler
        
        # Map of all sensors (key = sensor name, value = instance of Sensor)
        self.sensors = {}
        
        # Create watchers
        self.continuouseWatcher = ContinuouseWatcher()
        self.discreteWatcher = DiscreteWatcher(self.scheduler)
        
        # Watch
        self.__regularUpdateWrapper()   
        

    def __regularUpdateWrapper(self):
        self.__updateSensors()
        self.scheduler.enter(5, 0, self.__regularUpdateWrapper, [])
     
     
    def __updateSensors(self):
        # Download all the sensors
        sensors = self.managementClient.getSensors(HOSTNAME)
    
        # Remove sensors
        sensorsMap = dict([(k, None) for k in sensors])
        for test in self.sensors.keys():
            if test not in sensorsMap:
                self.__disableSensor(test)
                
        # Get all new sensors
        toAdd = [item for item in sensors if item not in self.sensors]
        
        # Update configuration for the remaining sensors
        for sensor in toAdd:
            self.__setupSensor(sensor)
   
   
    def __setupSensor(self, sensorName):
        sensor = Sensor(sensorName, self.loggingClient, self.managementClient)
        launch = sensor.configure()
        self.sensors[sensorName] = sensor
        
        print 'Setting up sensor %s' % (sensorName)
        
        if launch:
            if sensor.sensorType() == Sensor.CONTINUOUSE:
                self.continuouseWatcher.addSensor(sensor)
            elif sensor.sensorType() == Sensor.DISCRETE:
                self.discreteWatcher.addSensor(sensor)


    def __disableSensor(self, sensorName):
        print 'disabling sensor %s' % (sensorName)
        
        sensor = self.sensors[sensorName]
        if sensor.sensorType() == Sensor.CONTINUOUSE:
            self.continuouseWatcher.shutdownSensor(sensor)
        elif sensor.sensorType() == Sensor.DISCRETE:
            self.discreteWatcher.shutdownSensor(sensor)
        
        self.sensors.pop(sensorName)


    def join(self):
        self.continuouseWatcher.join()
        self.discreteWatcher.join()


def main():
    print 'Hostname of this machine: %s' % (HOSTNAME)
    print 'Main thread id: %i' % (thread.get_ident())
    
    # Make socket
    trasportManagement = TSocket.TSocket('131.159.41.171', 7931)
    transportLogging = TSocket.TSocket('131.159.41.171', 7921)
    
    # Buffering is critical. Raw sockets are very slow
    trasportManagement = TTransport.TBufferedTransport(trasportManagement)
    transportLogging = TTransport.TBufferedTransport(transportLogging) 
    
    # Setup the clients
    managementClient = ManagementService.Client(TBinaryProtocol.TBinaryProtocol(trasportManagement));
    loggingClient = CollectService.Client(TBinaryProtocol.TBinaryProtocol(transportLogging));  
    
    # Open the transports
    trasportManagement.open();
    transportLogging.open(); 
    
    # Register this host
    registerSensorHub(managementClient, HOSTNAME)
    
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


# jump into the main method
if __name__ == '__main__':
    main()
