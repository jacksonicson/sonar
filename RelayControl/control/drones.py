from mako.template import Template
import os
import shutil
import string

######################
## CONFIGURATION    ##
DRONE_DIR = 'drones'
######################

class Drone(object):
    def __init__(self, name, data):
        self.name = name
        self.data = data

        
def prepare_drone(name, template, **properties):
    path = os.path.join(os.getcwd(), DRONE_DIR, name, template + '.template')
    mytemplate = Template(filename=path, module_directory='/tmp/mako_modules')
    result = mytemplate.render(**properties)
    
    path = os.path.join(os.getcwd(), DRONE_DIR, name, template)
    tmpl_file = open(path, 'wb')
    tmpl_file.write(result)
    tmpl_file.close()
    
        
def load_drone(name):
    print 'loading drone %s' % (name)
    droneFile = open(os.path.join(DRONE_DIR, name + '.zip'), 'rb')
    drone = droneFile.read()
    droneFile.close()
    
    drone = Drone(name, drone)
    return drone


def create_drone(name):
    path = os.path.join(os.getcwd(), DRONE_DIR, name)
    zip_path = os.path.join(os.getcwd(), DRONE_DIR, name + '.zip')
    
    if os.path.exists(zip_path):
        os.remove(zip_path)
        
    shutil.make_archive(path, 'zip', path)
    return name + '.zip'


def __clean(path):
    for subdir in os.listdir(path):
        subpath = os.path.join(path, subdir)
        if os.path.isfile(subpath) == False:
            continue
            
        if string.find(subdir, '.zip') != -1:
            os.remove(subpath)

def build_all_drones():
    print 'Running drone builder...'
    
    # Works on the drone directory
    path = os.getcwd() 
    path = os.path.join(path, DRONE_DIR)
    
    # Remove all zip files in the drone directory
    __clean(path)
    
    # Creates drone packages
    for subdir in os.listdir(path):
        if os.path.isfile(os.path.join(path, subdir)):
            continue
        
        drone_path = os.path.join(path, subdir)
        create_drone(drone_path)

def main():
    build_all_drones()
        
if __name__ == '__main__':
    main() 
