from collector import ttypes
from constants import SENSOR_DIR, HOSTNAME
import os
import subprocess
import thread
import time

class Sensor:
    
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
        
