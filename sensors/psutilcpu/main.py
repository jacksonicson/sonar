import psutil
import sys
import time

NAME = 'psutilcpu'

while True:
    line = ''
    line += str(time.time()) + ','
    line += NAME + ','
    
    value = str(psutil.cpu_percent(interval=3))
    line += value
    
    print (line)
    sys.stdout.flush()
