from sensorhub import sensorhub
import traceback

# jump into the main method
if __name__ == '__main__':
    try:
        sensorhub.main()
    except Exception as e:
        print 'Exception in SensorHub, exiting'
        print traceback.format_exc()
