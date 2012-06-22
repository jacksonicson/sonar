import os
import shutil
import string
import cli
import yaml
from optparse import OptionParser
from collector import CollectService, ManagementService, ttypes
from thrift import Thrift
from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport

def configure(sensor, path):
    conf = os.path.join(path, 'conf.yaml')
    if os.path.exists(conf):
        yf = open(conf, 'r')
        content = yaml.load(yf)
        yf.close()
        
        interval = 0
        if hasattr(content, 'interval'):
            interval = int(content.interval)
        
        transport = TSocket.TSocket('131.159.41.171', 7931)
        transport = TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        client = ManagementService.Client(protocol);
        transport.open();
        
        config = ttypes.SensorConfiguration()
        config.interval = interval
        client.setSensorConfiguration(sensor, config)
        
        transport.close()
        print 'configuration applied'
        
        print content
        
    pass

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
    path = os.path.dirname(__file__)
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