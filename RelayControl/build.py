import os
import shutil
import string

DRONE_DIR = 'drones'

def createDrone(name, path):
    print 'creating zip %s.zip ...' % (name)
    shutil.make_archive(name, 'zip', path)
    return name + '.zip'


def clean(path):
    for subdir in os.listdir(path):
        if os.path.isfile(os.path.join(path, subdir)) == False:
            continue
        
        if string.find(subdir, '.zip') != -1:
            print 'delete %s' % (subdir)
            os.remove(os.path.join(path, subdir))


def main():
    # Works on the drone directory
    path = os.getcwd() 
    path = os.path.join(path, DRONE_DIR)
    print path
    
    # Remove all zip files in the drone directory
    clean(path)
    
    # Creates drone packages
    for subdir in os.listdir(path):
        if os.path.isfile(os.path.join(path, subdir)):
            continue
    
        sensorPath = os.path.join(path, subdir)
        targetPath = os.path.join(path, subdir)
        package = createDrone(targetPath, sensorPath)
        package = os.path.join(path, package)
        
if __name__ == '__main__':
    main() 
