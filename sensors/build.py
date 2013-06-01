import os
import shutil
import string
import cli
import yaml
from optparse import OptionParser
import connect
from collector import ttypes

def configure(sensor, path):
    conf = os.path.join(path, 'conf.yaml')
    if os.path.exists(conf):
        # Reading yaml file
        yf = open(conf, 'r')
        content = yaml.load(yf)
        yf.close()
        
        config = ttypes.SensorConfiguration()
        if 'interval' in content:
            config.interval = int(content['interval'])

        if 'sensorType' in content:
            config.sensorType = ttypes.SensorType._NAMES_TO_VALUES[content['sensorType']]
        else:
            config.sensorType = ttypes.SensorType._NAMES_TO_VALUES['METRIC']
            
        parameters = []
        if 'params' in content:
            for key in content['params'].keys():
                param = ttypes.Parameter()
                param.key = key
                param.value = str(content['params'][key])
                parameters.append(param)
        config.parameters = parameters
        
        # Connect with management interface
        transport, client = connect.openClient()
        
        # Update configuration
        client.updateSensorConfiguration(sensor, config, [])
        
        # Close transport
        connect.closeClient(transport)
        
        print 'Configuration applied'

def createSensor(name, path):
    print 'creating zip...'
    shutil.make_archive(name, 'zip', path)
    return name + '.zip'

def clean(path):
    for subdir in os.listdir(path):
        if os.path.isfile(subdir) == False:
            continue
        
        if string.find(subdir, '.zip') != -1:
            print 'removing %s' % (subdir)
            os.remove(os.path.join(path, subdir))

def deploy(name, package):
    cli.deploy(name, package)

def main():
    path = os.getcwd() 
    clean(path)
    for subdir in os.listdir(path):
        if os.path.isfile(subdir):
            continue
        elif subdir == 'collector':
            continue
    
        sensorPath = os.path.join(path, subdir)
        package = createSensor(subdir, sensorPath)
        package = os.path.join(path, package)
        deploy(subdir, package)
        configure(subdir, sensorPath)
        
if __name__ == '__main__':
    main() 
