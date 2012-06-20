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
import signal
import string
import thread
import threading
import time
import zipfile


class Sensor(object):

    CONTINUOUSE = 0
    DISCRETE = 1
    VALID_MAINS = ('main', 'main.exe', 'main.py', 'main.sh') 
    
    def __init__(self, name, loggingClient, managementClient):
        self.loggingClient = loggingClient
        self.managementClient = managementClient
        self.name = name
        self.md5 = None
        self.__configured = False
    
    def receive(self, line):
        # each line has the format
        # timestamp, name, value
        # timestamp = UNIX timestamp in seconds since epoch
        # name = (string value | 'none')
        # value = float value 
        
        # Check line structure
        elements = string.split(line, ',')
        if len(elements) != 3:
            #print 'invalid line received: %s' % (line)
            return
            
        # Extract timestamp
        timestamp = None
        try:
            timestamp = long(float(elements[0])) 
        except ValueError as e:
            print 'error while parsing timestamp %s' % (elements[0])
            return
        
        # Extract and build name for the entry (combine with sensor name)
        name = None
        if elements[1] != 'none':
            name = self.name + '.' + elements[1]
        else:
            name = self.name
        
        # Extract value
        logValue = None
        try:
            logValue = float(elements[2])
        except ValueError as e:
            print 'error while parsing value %s: ' % (elements[2])
            return
            
        # Create new entry    
        ids = ttypes.Identifier();
        ids.timestamp = timestamp
        ids.sensor = name
        ids.hostname = HOSTNAME
        
        value = ttypes.MetricReading();
        value.value = logValue
        value.labels = []
            
        # Send message
        self.loggingClient.logMetric(ids, value)
        
        # Debug output    
        print "value %s" % (line)
       
    def sensorType(self):
        if self.__configured == False:
            print 'WARN: sensor is not configured, sensor type cannot be determined'
            return Sensor.DISCRETE
        
        if self.settings.interval > 0: 
            return Sensor.DISCRETE

        return Sensor.CONTINUOUSE
        
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
            print 'WARN: configuration is not active'
            # return False

        # Get MD5 value
        self.md5 = self.__download()
        
        # Update internal configured status
        self.__configured = True
        
        return True
    
    
    def validate(self):
        exists = False
        
        for main in Sensor.VALID_MAINS:
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
        except Exception as e:
            print 'Error while creating target directory'
            print e
        
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
        for main in Sensor.VALID_MAINS:
            target = os.path.join(SENSOR_DIR, sensor.name, main)
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
            ending = mainFile[(index + 1):]
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
                executable = [path, ]
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
            
   
class DiscreteWatcher(Thread, ProcessLoader):
    
    def __init__(self, shutdownHandler):
        self.sensors = []
        shutdownHandler.addHandler(self.shutdown)
        
        self.start()

    def run(self):
        print 'Nees reimplementation of the scheduler'
        pass

    
    def addSensor(self, sensor):
        self.sensors.append(sensor)
        
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

    
    def shutdownSensor(self, sensor):
        self.sensors.remove(sensor)
    
    def shutdown(self):
        pass
        
   
class ContinuouseWatcher(Thread, ProcessLoader):
    
    SLEEP = 0.5
    
    def __init__(self, shutdownHandler):
        super(ContinuouseWatcher, self).__init__()
        
        self.lock = thread.allocate_lock()
        
        # list of sensors assigned to this watcher
        self.sensors = []
        
        # list of processes started by this watcher 
        self.processes = []
        
        # Alive flag
        self.alive = True

        # Register with shutdown events
        shutdownHandler.addHandler(self.shutdown)

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
        while self.alive:
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
            data = None
            try:
                data = select(streams, [], [], ContinuouseWatcher.SLEEP)[0]
            except: 
                break 
            
            self.lock.acquire()
            for i in range(0, len(data)):
                sensor = sensors[i]
                
                line = data[i]
                line = line.readline()
                line = line.strip().rstrip()
                
                sensor.receive(line)
                    
                    
            self.lock.release()

        # TODO: Guarantee that no process can be started after terminating
        print 'Continuouse thread terminates...'
        self.lock.acquire()
        for i in range(0, len(self.processes)):
            process = self.processes[i]
            print 'Terminating process %s ' % (self.sensors[i].name)
            process.kill()
        self.lock.release()
    
    
    def shutdown(self):
        # Exit main loop 
        self.alive = False
        
        # Wait until main loop is closing and taking all the processes with it
        if self.isAlive():
            print 'Waiting for all processes to terminate...'
            self.join()
            
        print 'continuouse watcher exited'
    

class SensorHub(object):
    def __init__(self, shutdownHandler, managementClient, loggingClient):
        self.managementClient = managementClient
        self.loggingClient = loggingClient

        # Register
        self.__registerSensorHub()
        
        # Register with shutdownHandler
        shutdownHandler.addHandler(self.shutdownHandler)
        
        # Map of all sensors (key = sensor name, value = instance of Sensor)
        self.sensors = {}
        
        # Create watchers
        self.continuouseWatcher = ContinuouseWatcher(shutdownHandler)
        self.discreteWatcher = DiscreteWatcher(shutdownHandler, self.scheduler)
        
        # Watch
        self.__regularUpdateWrapper()
        
        
    def __registerSensorHub(self):
        # Ensure that the hostname is registered
        print 'Adding host: %s' % (HOSTNAME)
        self.managementClient.addHost(HOSTNAME); 
        
        # Setup the self-monitoring SENSORHUB sensor
        sensor = self.managementClient.fetchSensor(SENSORHUB)
        if len(sensor) == 0: 
            print 'Deploying sensor: %s' % (SENSORHUB)
            self.managementClient.deploySensor(SENSORHUB, '  ')
            
        # Enable sensor for hostname
        print 'Enabling sensor: %s for host: %s' % (SENSORHUB, HOSTNAME)
        self.managementClient.setSensor(HOSTNAME, SENSORHUB, True)


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


    def shutdownHandler(self):
        pass
    
    
class WrapperLoggingClient(Thread, object):
    
    def __init__(self, shutdown, client):
        self.shutdown = shutdown
        self.lc = client
        
    def logMetric(self, ids, value):
        self.lock.acquire()
        try:
            self.lc.logMetric(ids, value)
        except:
            self.shutdown.shutdown()
            
        self.lock.release()


class ShutdownHandler(object):
    def __init__(self):
        self.callbacks = []
        self.condition = threading.Condition()

    def addHandler(self, callback):
        self.callbacks.append(callback)

    def shutdown(self):
        self.condition.acquire()
        self.condition.notify()
        self.condition.release()
            
    def wait(self):
        print 'Shutting down now...'
        self.condition.acquire()
        
        self.condition.wait()
        for callback in self.callbacks:
            callback() 
            
        self.condition.release()


def main():
    print 'Hostname of this machine: %s' % (HOSTNAME)
    print 'Main thread id: %i' % (thread.get_ident())
    
    # Make socket
    transportManagement = TSocket.TSocket('131.159.41.171', 7931)
    transportLogging = TSocket.TSocket('131.159.41.171', 7921)
    
    # Buffering is critical. Raw sockets are very slow
    transportManagement = TTransport.TBufferedTransport(transportManagement)
    transportLogging = TTransport.TBufferedTransport(transportLogging) 
    
    # Setup the clients
    managementClient = ManagementService.Client(TBinaryProtocol.TBinaryProtocol(transportManagement));
    loggingClient = CollectService.Client(TBinaryProtocol.TBinaryProtocol(transportLogging));  
    
    # Open the transports
    while True:
        try:
            transportManagement.open();
            transportLogging.open();
            break
        except Exception as e:
            print 'Retrying connection...'
            time.sleep(1)
    
    # Setup
    shutdown = ShutdownHandler()
    loggingClient = WrapperLoggingClient(shutdown, loggingClient)
    SensorHub(shutdown, managementClient, loggingClient)
    
    # React to kill signals
    print 'Handling sigterm and sigkill'
    def sigtermHandler(signum, frame):
        shutdown.shutdown()
    signal.signal(signal.SIGTERM, sigtermHandler)
    
    # Wait for shutdown
    shutdown.wait()
    


