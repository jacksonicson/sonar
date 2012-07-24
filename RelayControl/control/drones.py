import os
import shutil
import string

DRONE_DIR = 'drones'


def createDrone(name, path):
    shutil.make_archive(name, 'zip', path)
    return name + '.zip'


def clean(path):
    for subdir in os.listdir(path):
        subpath = os.path.join(path, subdir)
        if os.path.isfile(subpath) == False:
            continue
        
        if string.find(subdir, '.zip') != -1:
            os.remove(subpath)


def main():
    print 'Running drone builder...'
    
    # Works on the drone directory
    path = os.getcwd() 
    path = os.path.join(path, DRONE_DIR)
    
    # Remove all zip files in the drone directory
    clean(path)
    
    # Creates drone packages
    for subdir in os.listdir(path):
        if os.path.isfile(os.path.join(path, subdir)):
            continue
        
        targetPath = os.path.join(path, subdir)
        createDrone(targetPath, targetPath)
        
if __name__ == '__main__':
    main() 
