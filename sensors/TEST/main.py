import psutil
import sys
import time
import signal
import thread
import threading

cpu_times = psutil.cpu_times()
#  print "user time %i" % (cpu_times.user)

prev_bytes = 0

running = True

def sigtermHandler(signum, frame):
    global running
    running = False
        


def run():
    global running
    while running:
        line = ''
        line += str(time.time()) + ','
        line += 'none,'
        
        value = str(psutil.cpu_percent(interval=1))
        line += value
        
        print (line)
        sys.stdout.flush()
        
    print 'exited'
    sys.stdout.flush()


thread.start_new(run, ())



signal.signal(signal.SIGTERM, sigtermHandler)
try:
    signal.pause()
except KeyboardInterrupt:
    running = False

