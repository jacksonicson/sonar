import os
import shutil
import string
import yaml
from optparse import OptionParser

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

def main():
    path = os.getcwd() 
    clean(path)
    for subdir in os.listdir(path):
        if os.path.isfile(subdir):
            continue
        elif subdir == 'relay':
            continue
    
        sensorPath = os.path.join(path, subdir)
        package = createSensor(subdir, sensorPath)
        package = os.path.join(path, package)
        
if __name__ == '__main__':
    main() 
