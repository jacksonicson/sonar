import os
import zipfile
import shutil
from constants import SENSOR_DIR

def validate_sensor(sensor):
    exists = False
    target = SENSOR_DIR + sensor + "/main"
    exists |= os.path.exists(target)
    
    target = SENSOR_DIR + sensor + "/main.exe"
    exists |= os.path.exists(target)
    
    target = SENSOR_DIR + sensor + "/main.py"
    exists |= os.path.exists(target)
    
    return exists

def decompress_sensor(sensor):
    zf = zipfile.ZipFile(sensor + ".zip")
    
    target = SENSOR_DIR + sensor + "/"
    
    if os.path.exists(target):
        print 'removing sensor directory: ' + target
        shutil.rmtree(target, True)
    
    try:
        os.makedirs(target)
    except:
        pass
    
    for info in zf.infolist():
        print info.filename

        if info.filename.endswith('/'):
            try:
                print 'creating directory ' + info.filename
                os.makedirs(target + info.filename)
            except:
                print 'fail'
            continue
        
        cf = zf.read(info.filename)
        
        f = open(target + info.filename, "wb")
        f.write(cf)
        f.close()
        
    zf.close()