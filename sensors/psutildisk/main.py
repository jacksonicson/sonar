import psutil
import sys
import time

NAME = sys.argv[1]

last_write_count = 0
last_write_bytes = 0
last_read_count = 0
last_read_bytes = 0

while True:
    diskio = psutil.disk_io_counters(perdisk=False)
    
    read_count = diskio.read_count
    if last_read_count == 0:
        last_bytes_recv = read_count
    
    read_bytes = diskio.read_bytes
    if last_read_bytes == 0:
        last_read_byts = read_bytes
    
    write_count = diskio.write_count
    if last_write_count == 0:
        last_write_count = write_count

    write_bytes = diskio.write_bytes
    if last_write_bytes == 0:
        last_write_bytes = write_bytes
    
    wait = 3
    delta_read_count = (read_count - last_read_count) / (3 * 1024)
    delta_read_bytes = (read_bytes - last_read_bytes) / (3 * 1024)
    delta_write_count = (write_count - last_write_count) / (3 * 1024)
    delta_write_bytes = (write_bytes - last_write_bytes) / (3 * 1024)
    
    line = NAME + ','
    line += str(time.time()) + ','
    line += 'readcount' + ','
    line += 'none' + ','
    value = str(delta_read_count)
    line += value
    print (line)
    
    line = NAME + ','
    line += str(time.time()) + ','
    line += 'writecount' + ','
    line += 'none' + ','
    value = str(delta_write_count)
    line += value
    print (line)
    
    line = NAME + ','
    line += str(time.time()) + ','
    line += 'readbytes' + ','
    line += 'none' + ','
    value = str(delta_read_bytes)
    line += value
    print (line)
    
    line = NAME + ','
    line += str(time.time()) + ','
    line += 'writebytes' + ','
    line += 'none' + ','
    value = str(delta_write_bytes)
    line += value
    print (line)
    
    line = NAME + ','
    line += str(time.time()) + ','
    line += 'readtime' + ','
    line += 'none' + ','
    value = str(diskio.read_time)
    line += value
    print (line)
    
    line = NAME + ','
    line += str(time.time()) + ','
    line += 'writetime' + ','
    line += 'none' + ','
    value = str(diskio.write_time)
    line += value
    print (line)
    
    sys.stdout.flush()
    time.sleep(wait)
