import psutil
import sys
import time

NAME = sys.argv[1]

while True:
    diskio = psutil.disk_io_counters(perdisk=False)

    line = NAME + ','
    line += str(time.time()) + ','
    line += 'readcount' + ','
    value = str(diskio.read_count)
    line += value
    print (line)
    
    line = NAME + ','
    line += str(time.time()) + ','
    line += 'writecount' + ','
    value = str(diskio.write_count)
    line += value
    print (line)
    
    line = NAME + ','
    line += str(time.time()) + ','
    line += 'readbytes' + ','
    value = str(diskio.read_bytes)
    line += value
    print (line)
    
    line = NAME + ','
    line += str(time.time()) + ','
    line += 'writebytes' + ','
    value = str(diskio.write_bytes)
    line += value
    print (line)
    
    line = NAME + ','
    line += str(time.time()) + ','
    line += 'readtime' + ','
    value = str(diskio.read_time)
    line += value
    print (line)
    
    line = NAME + ','
    line += str(time.time()) + ','
    line += 'writetime' + ','
    value = str(diskio.write_time)
    line += value
    print (line)
    
    sys.stdout.flush()
    time.sleep(3)
