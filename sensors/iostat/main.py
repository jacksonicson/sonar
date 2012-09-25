import subprocess
from subprocess import PIPE
import sys
import re
import time
import signal

# Read arguments
NAME = sys.argv[1]

if len(sys.argv) > 1:
    DEVICE = sys.argv[2]
    DEVICE = DEVICE.replace('device=', '')

command = ['iostat', '-x', '-d', '3', DEVICE]
process = subprocess.Popen(command, shell=False, stdout=PIPE, bufsize=1, universal_newlines=True)

running = True
while running:
    line = process.stdout.readline()
    line = line.strip().rstrip()
    if line == "":
        continue
    if line.find(DEVICE) != 0:
        continue
    
    elements = re.split('[\s]+', line)
    
    line = NAME + ','
    line += str(time.time()) + ','
    line += 'svctime' + ','
    line += 'none' + ','
    value = elements[12]
    line += value
    print (line)
    
    line = NAME + ','
    line += str(time.time()) + ','
    line += 'await' + ','
    line += 'none' + ','
    value = elements[9]
    line += value
    print (line)
    
    line = NAME + ','
    line += str(time.time()) + ','
    line += 'avgqu-sz' + ','
    line += 'none' + ','
    value = elements[8]
    line += value
    print (line)
    

def handleSigTERM():
    running = False
signal.signal(signal.SIGTERM, handleSigTERM)
signal.signal(signal.SIGKILL, handleSigTERM)  
