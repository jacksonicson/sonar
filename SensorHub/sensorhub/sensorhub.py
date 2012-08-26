from collector import CollectService, ManagementService, ttypes
from constants import HOSTNAME
from select import select
from subprocess import Popen, PIPE
from threading import Thread
from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport
import os
import sched
import shutil
import signal
import string
import tempfile
import thread
import threading
import time
import traceback
import zipfile

##########################
## Configuration        ##
COLLECTOR_IP = 'monitor0'
MANAGEMENT_PORT = 7931
LOGGING_PORT = 7921
DEBUG = False
##########################

class Sensor(object):

    CONTINUOUSE = 0
    DISCRETE = 1
    INVALID = 2
    VALID_MAINS = ('main', 'main.exe', 'main.py', 'main.sh') 
    
    def __init__(self, name, loggingClient, managementClient):
        self.loggingClient = loggingClient
        self.managementClient = managementClient
        self.name = name
        self.md5 = None
        self.__configured = False
    
    # Threadsafe
    def receive(self, line):
        raise NotImplementedError("Please Implement this method")
              
    def sensorType(self):
        if self.__configured == False:
            print 'WARN: sensor is not configured, sensor type cannot be determined'
            return Sensor.INVALID
        
        if self.settings.interval > 0: 
            return Sensor.DISCRETE
        elif self.settings.interval == 0:
            return Sensor.CONTINUOUSE
        
        return Sensor.INVALID
        
        
    def __download(self):
        # Get the MD5 value of the binary
        testMd5 = self.managementClient.sensorHash(self.name)
        
        # Check if MD5 changed since the last fetch
        if self.md5 == testMd5:
            return self.md5
                
        # Ensure that the temp directoy is there
        tmpdir = os.path.join(tempfile.gettempdir(), 'sonar')
        if os.path.exists(tmpdir) == False:
            os.makedirs(tmpdir)        
                
        # Remove old sensor package
        tmpfile = os.path.join(tempfile.gettempdir(), 'sonar', self.name + '.zip')
        if os.path.exists(tmpfile):
            os.remove(tmpfile)
            
        # Download sensor
        data = self.managementClient.fetchSensor(self.name)
        z = open(tmpfile, 'wb')
        z.write(data)
        z.close()
        
        # Decompress sensor package      
        status = self.__decompress()
        if status == False:
            return None
        
        return testMd5
        
        
    def configure(self):
        # Only accept sensors with binaries
        if not self.managementClient.hasBinary(self.name):
            print 'Skipping sensor %s, missing binary' % (self.name)
            return False

        # Download settings
        bundledConfiguration = self.managementClient.getBundledSensorConfiguration(self.name, HOSTNAME)
        self.settings = bundledConfiguration.configuration
        self.labels = bundledConfiguration.labels
        
        # Just for safety - this should never match because inactive sensors are
        # handled by the synchronization process
        if bundledConfiguration.active == False:
            print 'WARN: configuration is not active'

        # Get MD5 value
        self.md5 = self.__download()
        if self.md5 == None:
            print 'ERR: while downloading and unzipping sensor'
            return False
        
        # Update internal configured status
        self.__configured = True
        
        return True
    
    
    def validate(self):
        exists = False
        
        for main in Sensor.VALID_MAINS:
            target = os.path.join(tempfile.gettempdir(), 'sonar', self.name, main)
            exists |= os.path.exists(target)
        
        return exists

    
    def __decompress(self):
        zf = zipfile.ZipFile(os.path.join(tempfile.gettempdir(), 'sonar', self.name + ".zip"))
        
        target = os.path.join(tempfile.gettempdir(), 'sonar', self.name)
        
        if os.path.exists(target):
            shutil.rmtree(target, True)
        
        try:
            print 'mkdir: %s' % (target)
            os.makedirs(target)
        except Exception as e:
            print 'Error while creating target directory'
            return False
        
        for info in zf.infolist():
            print info.filename
    
            if info.filename.endswith('/'):
                try:
                    os.makedirs(os.path.join(target, info.filename))
                except Exception as e:
                    print 'error while decompressing files %s' % (e)
                    return False
                    
                continue
            
            cf = zf.read(info.filename)
            f = open(os.path.join(target, info.filename), "wb")
            f.write(cf)
            f.close()
            
        zf.close()
        
        return True

class LogSensor(Sensor):
    def __init__(self, name, loggingClient, managementClient):
        super(LogSensor, self).__init__(name, loggingClient, managementClient)

    # Threadsafe
    def receive(self, line):
        # each line has the format
        # sensor, timestamp, programName, logMessage
        # sensor = The name of the sensor which is passed to the process as first argument
        # timestamp = UNIX timestamp in seconds since epoch
        # programName = name of the program generating the logs 
        # logMessage = the log message itself

        
        elements = string.split(line, ',')

        # Extract timestamp
        timestamp = None
        try:
            timestamp = long(float(elements[1])) 
        except ValueError as e:
            print 'error while parsing timestamp %s' % (elements[0])
            return
            
        # sensor name
        name = self.name

        # program name
        programName = None
        try:
            programName = elements[2]
        except ValueError as e:
            print 'error while parsing programname %s' % (elements[1])
            return
           
        # Extract value
        logValue = None
        try:
            logValue = elements[3]
        except ValueError:
            print 'error while parsing value %s: ' % (elements[2])
            return
                
        # Create new entry    
        ids = ttypes.Identifier()
        ids.timestamp = timestamp
        ids.sensor = name
        ids.hostname = HOSTNAME
            
        value = ttypes.LogMessage()
        value.logLevel = 5
        value.logMessage = logValue
        value.programName = programName
        value.timestamp = timestamp
                
        # Send message
        self.loggingClient.logMessage(ids, value)

        # Debug output
        if DEBUG:    
            print "value is %s" % (line)

        
    
class MetricSensor(Sensor):
    def __init__(self, name, loggingClient, managementClient):
        super(MetricSensor, self).__init__(name, loggingClient, managementClient)

    # Threadsafe
    def receive(self, line):
        # each line has the format
        # sensor, timestamp, name, value
        # sensor = The name of the sensor which is passed to the process as first argument
        # timestamp = UNIX timestamp in seconds since epoch
        # name = string value or 'none' if no subname for the sensor is given 
        # value = float value which shall be logged
        
        # Check line structure
        elements = string.split(line, ',')
        if len(elements) != 5:
            print 'invalid line received: %s' % (line)
            return
                    
        # Extract timestamp
        timestamp = None
        try:
            timestamp = long(float(elements[1])) 
        except ValueError as e:
            print 'error while parsing timestamp %s' % (elements[0])
            return
                
        # Extract and build name for the entry (combine with sensor name)
        name = None
        if elements[2] == 'none':
            name = self.name
        else:
            name = self.name + '.' + elements[2]
                
        # Overrides the hostname
        hostname = None
        if elements[3] == 'none':
            hostname = HOSTNAME
        else:
            hostname = elements[3]
                
        # Extract value
        logValue = None
        try:
            logValue = float(elements[4])
        except ValueError:
            print 'error while parsing value %s: ' % (elements[4])
            return
                    
        # Create new entry    
        ids = ttypes.Identifier();
        ids.timestamp = timestamp
        ids.sensor = name
        ids.hostname = hostname
                
        value = ttypes.MetricReading();
        value.value = logValue
        value.labels = []
                    
        # Send message
        self.loggingClient.logMetric(ids, value)

        # Debug output
        if DEBUG:    
            print "value %s" % (line)

class ProcessLoader(object):
    def newProcess(self, sensor):
        # determine the executable
        mainFile = None
        for main in Sensor.VALID_MAINS:
            target = os.path.join(tempfile.gettempdir(), 'sonar', sensor.name, main)
            if os.path.exists(target):
                mainFile = main
                break
            
        # break if there is no main file
        if mainFile == None:
            print 'missing main file for sensor %s' % (sensor.name)
            return
        
        # determine the executable (python, ..)
        executable = None
        main = None
        try:    
            index = string.rindex(mainFile, '.')
            ending = mainFile[(index + 1):]
            if ending == 'py':
                executable = 'python'
                main = 'main.py'
            elif ending == 'sh':
                executable = 'bash'
                main = 'main.sh'
            elif ending == 'exe':
                executable = None
                main = 'main.exe'
        except ValueError:
            executable = None
            main = None
        
        # create a new process 
        try:
            path = os.path.join(tempfile.gettempdir(), 'sonar', sensor.name, main)
            
            # configure executable and main file
            if executable is None:
                executable = [path, sensor.name]
            else:
                executable = [executable, path, sensor.name]

            # check if the sensor configuration has parameters
            if sensor.settings.parameters is not None:
                paramLen = len(sensor.settings.parameters)
                if paramLen > 0:
                    print 'sensor parameter exists, appending same as command line arguments'
                    for parameter in sensor.settings.parameters:
                        paramValue = parameter.key + '=' + parameter.value
                        executable.append(paramValue) 

            process = Popen(executable, stdout=PIPE, bufsize=1, universal_newlines=True)
            
            print 'PID %i' % (process.pid)
            return process
        except Exception, e:
            print 'error starting process: %s' % (e)
            return None
    
    
    def kill(self, process):
        try:
            process.kill()
        except Exception as e:
            print 'error while killing process %s' % (e)
            
   
class DiscreteWatcher(Thread, ProcessLoader):
    
    def __init__(self, shutdownHandler):
        super(DiscreteWatcher, self).__init__()
        
        self.sensors = []
        self.lock = thread.allocate_lock()
        
        shutdownHandler.addHandler(self.shutdown)
        
        self.running = True
        self.start()
        print 'forged: discrete watcher'


    def run(self):
        self.lock.acquire()
        self.scheduler = sched.scheduler(time.time, time.sleep)
        for sensor in self.sensors:
            self.scheduler.enter(sensor.settings.interval, 0, self.__processSensor, [sensor])
        self.lock.release()
        
        while self.running:
            self.scheduler.run()
            time.sleep(1)

    def addSensor(self, sensor):
        self.lock.acquire()
        
        self.sensors.append(sensor)
        if hasattr(self, 'scheduler'):
            self.scheduler.enter(sensor.settings.interval, 0, self.__processSensor, [sensor])
            
        self.lock.release()

    def __processSensor(self, sensor):
        # Filter removed sensors        
        if sensor not in self.sensors:
            return
        
        # Start a new process for each sensor call
        process = self.newProcess(sensor)
        if process != None:
            # get the standard output from the process
            line = process.communicate()[0]
            line = line.strip().rstrip()
            sensor.receive(line) 
        
        # Reschedule sensor
        self.lock.acquire()
        if self.running:
            self.scheduler.enter(sensor.settings.interval, 0, self.__processSensor, [sensor])
        self.lock.release()
    
    
    def shutdownSensor(self, sensor):
        self.lock.acquire()
        self.sensors.remove(sensor)
        self.lock.release()
    
    
    def shutdown(self):
        self.lock.acquire()
        self.running = False
        for i in self.scheduler.queue:
            self.scheduler.cancel(i)
        self.lock.release()
        
        while self.isAlive():
            self.join(timeout=3)
            print 'waiting for: discrete watcher'
        
        print 'joined: discrete watcher'
        
   
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

        # new Sensors
        self.newSensors = []
        
        # Start the thread
        self.start()
        print 'forged: continouse watcher'
        

    
    def addSensor(self, sensor):
        print 'Continuouse watcher adding sensor: %s' % (sensor)
        self.lock.acquire()
        self.newSensors.append(sensor)
        self.lock.release()


    def shutdownSensor(self, sensor):
        self.lock.acquire()
        
        for i in reversed(range(0, len(self.sensors))):
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
            tmpSensors = {}
            
            self.lock.acquire()
            
            for sensor in self.newSensors:
                process = self.newProcess(sensor)
                if process != None:
                    self.sensors.append(sensor)
                    self.processes.append(process)
                else:
                    print 'ERROR: Could not start process'
                    
            del self.newSensors[0:len(self.newSensors)]
            
            for i in range(0, len(self.processes)):
                streams.append(self.processes[i].stdout)
                tmpSensors[self.sensors[i].name] = self.sensors[i]
                
            self.lock.release()
        
            if len(streams) == 0:
                time.sleep(1)
                continue
            
            # Wait for receive and pick the stdout list
            data = None
            try:
                data = select(streams, [], [], ContinuouseWatcher.SLEEP)[0]
            except: 
                print 'stopping continuouse because of error in select'
                break 
            
            # Callback each sensor with the received data
            #self.lock.acquire()
            
            for i in range(0, len(data)):
                line = data[i]
                line = line.readline()
                line = line.strip().rstrip()

                index = line.find(',')
                if index == -1:
                    continue
                
                name = line[0:index]
                if name in tmpSensors:
                    tmpSensors[name].receive(line)
                else:
                    print 'no match'
                
                    
            #self.lock.release()

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
        while self.isAlive():
            self.join(timeout=3)
            print 'waiting for: continuouse watcher'
            
        print 'joined: continuouse watcher'
    

class SensorHub(Thread, object):
    def __init__(self, shutdown):
        super(SensorHub, self).__init__()
        
        # Synchronization condition
        self.condition = threading.Condition()
        
        # Private variables
        self.shutdown = shutdown
        
        # Connect
        self.__connect()
        
        # Register
        self.__registerSensorHub()
        
        # Map of all sensors (key = sensor name, value = instance of Sensor)
        self.sensors = {}
        
        # Create watchers
        self.continuouseWatcher = ContinuouseWatcher(shutdown)
        self.discreteWatcher = DiscreteWatcher(shutdown)
        
        # Watch
        self.running = True
        print 'forked: sensorhub'
        self.start()
        
        # shtudown
        self.shutdown.addHandler(self.__shutdownHandler)
        
      
    def __shutdownHandler(self):
        self.running = False
        self.condition.acquire()
        self.condition.notify()
        self.condition.release()
        
        while self.isAlive():
            self.join(timeout=3)
            print 'waiting for: sensorhub'
            
        print 'joined: sensorhub'
      
    def __connect(self):
        # Make socket
        transportManagement = TSocket.TSocket(COLLECTOR_IP, MANAGEMENT_PORT)
        transportLogging = TSocket.TSocket(COLLECTOR_IP, LOGGING_PORT)
        
        # Buffering is critical. Raw sockets are very slow
        transportManagement = TTransport.TBufferedTransport(transportManagement)
        transportLogging = TTransport.TBufferedTransport(transportLogging) 
        
        # Setup the clients
        self.managementClient = ManagementService.Client(TBinaryProtocol.TBinaryProtocol(transportManagement));
        self.loggingClient = CollectService.Client(TBinaryProtocol.TBinaryProtocol(transportLogging));
        self.loggingClient = WrapperLoggingClient(self.shutdown, self.loggingClient)  
        
        # Open the transports
        while True:
            try:
                transportManagement.open();
                transportLogging.open();
                break
            except Exception as e:
                print 'Retrying connection...'
                time.sleep(1)
        
        
    def __registerSensorHub(self):
        # Ensure that the hostname is registered
        print 'Adding host: %s' % (HOSTNAME)
        self.managementClient.addHost(HOSTNAME); 

    
    def run(self):
        self.condition.acquire()
        
        while self.running:
            try:
                self.__updateSensors()
                self.condition.wait(5)
            except Exception:
                self.condition.release()
                
                traceback.print_exc()
                self.shutdown.shutdown('exception while updating sensors')
                
                return
            
        self.condition.release()
    
    
    def __updateSensors(self):
        # Download all the sensors
        sensors = self.managementClient.getSensors(HOSTNAME)
    
        # Remove sensors
        sensorsMap = dict([(k, None) for k in sensors])
        for test in self.sensors.keys():
            if test not in sensorsMap:
                self.__disableSensor(test)
            
            
        # Check for sensor updates
        for test in self.sensors.keys():
            md5 = self.managementClient.sensorHash(test)
            if self.sensors[test].md5 != md5:
                print 'Updating sensor %s' % (test)
                self.__disableSensor(test)
                
        # Get all new sensors
        toAdd = [item for item in sensors if item not in self.sensors]
        
        # Update configuration for the remaining sensors
        for sensor in toAdd:
            self.__setupSensor(sensor)
   
   
    def __setupSensor(self, sensorName):
        sensorConfig = self.managementClient.getSensorConfiguration(sensorName)

        sensor = None
        if sensorConfig.sensorType == ttypes.SensorType.METRIC:
            sensor = MetricSensor(sensorName, self.loggingClient, self.managementClient)
        elif sensorConfig.sensorType == ttypes.SensorType.LOG:
            sensor = LogSensor(sensorName, self.loggingClient, self.managementClient)
        else:
            sensor = MetricSensor(sensorName, self.loggingClient, self.managementClient)

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

    
class WrapperLoggingClient(object):
    
    def __init__(self, shutdown, client):
        self.shutdown = shutdown
        self.lc = client
        self.lock = thread.allocate_lock()
        
    def logMetric(self, ids, value):
        self.lock.acquire()
        try:
            self.lc.logMetric(ids, value)
        except:
            self.shutdown.shutdown('exception while logging metric on collector')
            
        self.lock.release()

    def logMessage(self, ids, value):
        self.lock.acquire()
        try:
            self.lc.logMessage(ids, value)
        except:
            self.shutdown.shutdown('exception while logging metric on collector')
            
        self.lock.release()



class ShutdownHandler(object):
    def __init__(self):
        self.callbacks = []
        self.condition = threading.Condition()
        self.flag = False

    def addHandler(self, callback):
        self.callbacks.append(callback)

    def shutdown(self, msg='no reason'):
        print 'shutdown received: %s' % (msg)
        self.condition.acquire()
        self.flag = True
        self.condition.notify()
        self.condition.release()
            
    def run(self):
        print 'Waiting for shutdown event...'
        self.condition.acquire()

        # Spinning until shutdown signal is received        
        while self.flag == False:
            try:
                self.condition.wait(1)
            except KeyboardInterrupt:
                self.flag = True
                continue

        self.condition.release()
        
        # Shutdown
        print 'Shutting down now... ',
        for callback in self.callbacks:
            callback() 
        print 'OK'
            


def main():
    print 'Hostname of this machine: %s' % (HOSTNAME)
    print 'Main thread id: %i' % (thread.get_ident())
    
    # Setup
    shutdown = ShutdownHandler()
    SensorHub(shutdown)
    
    # React to kill signals
    def sigtermHandler(signum, frame):
        shutdown.shutdown('term signal received')
        
    signal.signal(signal.SIGTERM, sigtermHandler)
    
    # Wait for signals
    shutdown.run()

