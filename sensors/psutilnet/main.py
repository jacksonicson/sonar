import psutil
import sys
import time

NAME = sys.argv[1]

last_bytes_sent = 0
last_bytes_recv = 0

while True:
    iostat = psutil.network_io_counters()
    bytes_sent = iostat.bytes_sent
    if last_bytes_sent == 0:
        last_bytes_sent = bytes_sent
    
    bytes_recv = iostat.bytes_recv
    if last_bytes_recv == 0:
        last_bytes_recv = bytes_recv
    
    
    delta_bytes_sent = bytes_sent - last_bytes_sent
    delta_bytes_recv = bytes_recv - last_bytes_recv
    last_bytes_recv = bytes_recv
    last_bytes_sent = bytes_sent

    line = NAME + ','
    line += str(time.time()) + ','
    line += 'recv' + ','
    value = str(delta_bytes_recv)
    line += value
    print (line)

    line = NAME + ','
    line += str(time.time()) + ','
    line += 'sent' + ','
    value = str(delta_bytes_sent)
    line += value
    print (line)
    
    sys.stdout.flush()
    time.sleep(3)
