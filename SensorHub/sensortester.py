import sys
from sensorhub.sensorhub import Sensor, DiscreteWatcher, ContinuouseWatcher
from collector.ttypes import BundledSensorConfiguration, SensorConfiguration


class MockLoggingClient(object):
    
    def __init__(self):
        pass
    
    def logMetric(self, id, value):
        assert(id.timestamp != None)
        assert(id.timestamp > 0)
        
        assert(id.hostname != None)
        assert(len(id.hostname) > 1)
        
        assert(id.sensor != None)
        assert(len(id.sensor) > 1)
        
        assert(type(value.value) == type(0.0))
        
        print 'SUCCESS: Logging value'


class MockManagementClient(object):
    def __init__(self, file):
        self.file = file
    
    def query(self, query):
        pass
    
    def fetchSensor(self, name):
        print 'Loading sensor'
        f = open(self.file, 'rb')
        bb = f.read()
        f.close()
        return bb
    
    def sensorHash(self, name):
        return 0
    
    def deploySensor(self, name, file):
        pass
    
    def getAllSensors(self):
        pass
        
    def hasBinary(self, name):
        return True

    def getSensorLabels(self, sensor):
        pass
    
    def delSensor(self, sensor):
        pass    

    def setSensorLabels(self, sensor, labels):
        pass

    def setSensorConfiguration(self, sensor, configuration):
        pass    

    def addHost(self, hostname):
        pass
    
    def getAllHosts(self):
        pass    

    def delHost(self, hostname):
        pass    

    def setHostLabels(self, hostname, labels):
        pass
            
    def getLabels(self, hostname):
        pass
        
    def setSensor(self, hostname, sensor, activate):
        pass    

    def getSensors(self, hostname):
        pass    

    def getBundledSensorConfiguration(self, sensor, hostname):
        config = BundledSensorConfiguration()
        config.sensor = 'test'
        config.configuration = SensorConfiguration()
        config.configuration.interval = 1
        return config
        

class MockShutdownHandler(object):
    def addHandler(self, function):
        pass

def testContinuouse(sensorName, sensorFile):
    loggingClient = MockLoggingClient()
    managementClient = MockManagementClient(sensorFile)
    sensor = Sensor(sensorName, loggingClient, managementClient)
    sensor.configure()
    watcher = ContinuouseWatcher(MockShutdownHandler())
    watcher.addSensor(sensor)
    
    print 'Working...'
    import time
    time.sleep(10)
    
    print 'Shutting down...'
    watcher.shutdown()

def testDiscrete(sensorName, sensorFile):
    loggingClient = MockLoggingClient()
    managementClient = MockManagementClient(sensorFile)
    sensor = Sensor(sensorName, loggingClient, managementClient)
    sensor.configure()
    watcher = DiscreteWatcher(MockShutdownHandler())
    watcher.addSensor(sensor)
    
    print 'Working...'
    import time
    time.sleep(10)
    
    print 'Shutting down...'
    watcher.shutdown()
    
    

def main():
    if len(sys.argv) != 3:
        print 'Two arguments required: sensor-package, mode (0=continuouse, 1=discrete)'
        
    program = sys.argv[1]
    mode = sys.argv[2]
    
    if int(mode) == 0:
        testContinuouse('test', program)
    elif int(mode) == 1:
        testDiscrete('test', program)        
    
    pass


if __name__ == '__main__':
    main()