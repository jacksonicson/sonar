import psutil
import sys
import time

cpu_times = psutil.cpu_times()
#  print "user time %i" % (cpu_times.user)

prev_bytes = 0

while True:
    line = ''
    line += str(time.time()) + ','
    line += 'none,'
    
    try:
        value = str(psutil.cpu_percent(interval=1))
        line += value
    except:
        line += '0'
        print (line)
        sys.stdout.flush()
        break
    
    print (line)
    sys.stdout.flush()