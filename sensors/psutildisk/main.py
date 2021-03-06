import psutil
import sys
import time

NAME = sys.argv[1]

last_write_count = 0
last_write_bytes = 0
last_read_count = 0
last_read_bytes = 0
last_read_time = 0
last_write_time = 0

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
    
    read_time = diskio.read_time
    if last_read_time == 0:
        last_read_time = read_time
    
    write_time = diskio.write_time
    if last_write_time == 0:
        last_write_time = write_time
    
    wait = 3 # seconds
    delta_read_count = (read_count - last_read_count) / (wait * 1024)
    delta_read_bytes = (read_bytes - last_read_bytes) / (wait * 1024)
    delta_write_count = (write_count - last_write_count) / (wait * 1024)
    delta_write_bytes = (write_bytes - last_write_bytes) / (wait * 1024)
    delta_read_time = (read_time - last_read_time) / (wait)
    delta_write_time = (write_time - last_write_time) / (wait)
    
    last_read_count = read_count
    last_read_bytes = read_bytes
    last_write_count = write_count
    last_write_bytes = write_bytes
    last_read_time = read_time
    last_write_time = write_time
    
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
    value = str(delta_read_time)
    line += value
    print (line)
    
    line = NAME + ','
    line += str(time.time()) + ','
    line += 'writetime' + ','
    line += 'none' + ','
    value = str(delta_write_time)
    line += value
    print (line)
    
    sys.stdout.flush()
    time.sleep(wait)
