import psutil
import sys
import time

NAME = 'psutilmem'

while True:
    memusage = psutil.phymem_usage()
    memusage = memusage.percent
    
    line = ''
    line += str(time.time()) + ','
    line += NAME + '.phymem' + ','
    value = str(memusage)
    line += value
    print (line)
    
    virtusage = psutil.virtmem_usage()
    virtusage = virtusage.percent
    
    line = ''
    line += str(time.time()) + ','
    line += NAME + '.virtmem' + ','
    value = str(virtusage)
    line += value
    print (line)
    
    sys.stdout.flush()
    time.sleep(3)
