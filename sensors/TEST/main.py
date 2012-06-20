import psutil
import sys
import time

line = ''
line += str(time.time()) + ','
line += 'none,'

value = str(psutil.cpu_percent(interval=1))
line += value

print (line)
sys.stdout.flush()
        