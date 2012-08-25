import psutil
import sys
import time

NAME = sys.argv[1]

while True:
    memusage = psutil.phymem_usage()
    memusage = memusage.percent
    
    line = NAME + ','
    line += str(time.time()) + ','
    line += 'phymem' + ','
    line += 'none' + ','
    value = str(memusage)
    line += value
    print (line)
    
    virtusage = psutil.virtmem_usage()
    virtusage = virtusage.percent
    
    line = NAME + ','
    line += str(time.time()) + ','
    line += 'virtmem' + ','
    line += 'none' + ','
    value = str(virtusage)
    line += value
    print (line)
    
    sys.stdout.flush()
    time.sleep(3)
