import psutil
import sys
import time

NAME = sys.argv[1]

while True:
    line = NAME + ','
    line += str(time.time()) + ','
    line += 'none' + ','
    line += 'none' + ','
    
    value = str(psutil.cpu_percent(interval=3))
    line += value
    
    print (line)
    sys.stdout.flush()

