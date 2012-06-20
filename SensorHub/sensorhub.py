from sensorhub import sensorhub
import sys

# jump into the main method
if __name__ == '__main__':
    try:
        sensorhub.main()
        sys.stdout.flush()
        print 'exiting now'
    except Exception as e:
        print 'Exception in SensorHub, exiting'
        
