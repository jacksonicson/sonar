import psutil
import sys
import time

NAME = 'psutilmem'

while True:
    diskio = psutil.disk_io_counters(perdisk=False)

    line = ''
    line += str(time.time()) + ','
    line += NAME + '.readcount' + ','
    value = str(diskio.read_count)
    line += value
    print (line)
    
    line = ''
    line += str(time.time()) + ','
    line += NAME + '.writecount' + ','
    value = str(diskio.write_count)
    line += value
    print (line)
    
    line = ''
    line += str(time.time()) + ','
    line += NAME + '.readbytes' + ','
    value = str(diskio.read_bytes)
    line += value
    print (line)
    
    line = ''
    line += str(time.time()) + ','
    line += NAME + '.writebytes' + ','
    value = str(diskio.write_bytes)
    line += value
    print (line)
    
    line = ''
    line += str(time.time()) + ','
    line += NAME + '.readtime' + ','
    value = str(diskio.read_time)
    line += value
    print (line)
    
    line = ''
    line += str(time.time()) + ','
    line += NAME + '.writetime' + ','
    value = str(diskio.write_time)
    line += value
    print (line)
    
    sys.stdout.flush()
    time.sleep(3)
