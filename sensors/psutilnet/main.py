import psutil
import sys
import time

NAME = sys.argv[1]

last_bytes_sent = 0
last_bytes_recv = 0

keys = ('br0', 'eth0') 

while True:
    iostat = psutil.network_io_counters(pernic=True)
    for key in keys:
        if not iostat.has_key(key):
            continue
        
        entry = iostat[key]
        
        bytes_sent = entry.bytes_sent
        if last_bytes_sent == 0:
            last_bytes_sent = bytes_sent
        
        bytes_recv = entry.bytes_recv
        if last_bytes_recv == 0:
            last_bytes_recv = bytes_recv
        
        wait = 3
        
        delta_bytes_sent = 0
        delta_bytes_recv = 0
        if bytes_sent >= last_bytes_sent:
            delta_bytes_sent = (bytes_sent - last_bytes_sent) / wait
            delta_bytes_recv = (bytes_recv - last_bytes_recv) / wait
        else:
            continue
        
        last_bytes_recv = bytes_recv
        last_bytes_sent = bytes_sent
    
        # To KBit per second
        delta_bytes_sent = delta_bytes_sent / 1024
        delta_bytes_recv = delta_bytes_recv / 1024
    
        line = NAME + ','
        line += str(time.time()) + ','
        line += key + '.recv' + ','
        line += 'none' + ','
        
        value = str(delta_bytes_recv)
        line += value
        print (line)
    
        line = NAME + ','
        line += str(time.time()) + ','
        line += key + '.sent' + ','
        line += 'none' + ','
        
        value = str(delta_bytes_sent)
        line += value
        print (line)
        
        sys.stdout.flush()
        time.sleep(wait)
