"""
/*******************************************************************************
 * Copyright (c) 2010 Andreas Wolke.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Andreas Wolke - initial API and implementation and initial documentation
 *******************************************************************************/
"""
import os
import string
import sys

def getClasspathSeparator():
    separator = ";"
    if os.name == 'posix':
        separator = ":"
    
    return separator

def loadClasspath(file, additionalCp):
    # Load the classpath from classpath.txt
    file = open(sys.path[0] + file, "r")
    lines = file.readlines()
    
    # Load classpath separator
    separator = getClasspathSeparator()
    
    # Read classpath from file
    classpath = ""
    for line in lines:
        line = line.replace("\r\n", "")
        line = line.replace("\n", "")
        line = line.replace("\r", "")
        classpath += line + separator
    
    # Add the classpath from the argument    
    for additional in additionalCp:
        classpath += additional + separator
    
    return classpath    


def runCollector(args):
    mainClass = 'de.tum.in.sonar.collector.Collector'
    
    classpath = []
    classpath.append("collector.jar")
    classpath = loadClasspath('/classpath.txt', classpath)
    
    print classpath
    
    params = []
    params.append('java')
    
    params.append('-Xms30m')
    params.append('-Xmx100m')
    
    params.append('-classpath')
    params.append(classpath)
    
    params.append(mainClass)
    
    print args
    params.extend(args)
    
    os.chdir(sys.path[0])
    os.execvp("java", params)


def writePid(name):
    pid = os.getpid()
    pidfile = name + ".pid"
    print "Writing %i to %s" % (pid, pidfile)
    
    file = open(pidfile, 'w')
    file.write(str(pid))
    file.close()


def checkPid(name):
    pidfile = name + ".pid"
    try:
        with open(pidfile) as f: pass
    except IOError as e:
        return True
    
    print "PID file for process %s does already exist" % (pidfile)
    return False


def killAll():
    dirlist = os.listdir(os.curdir)
    for item in dirlist:
        if item.find('.pid') != -1:
            index = item.find('.pid')
            name = item[0:index]
            
            file = open(item)
            pid = int(file.readline())
            file.close()
            
            print "Killing %s with pid %i" % (name, pid)
            
            try:
                os.kill(int(pid), 15)
            except:
                print 'unable to kill process'
            
            toremove = os.curdir + os.sep + item
            print "Deleting file %s" % toremove
            os.remove(toremove)



def main(args):
    name = args[1]
    print "Option %s" % name

    if name == 'kill':
        print 'shutting down...'
        killAll()
        return

    # Check if the process is already running
    if checkPid(name) is False:
        print 'exiting now'
        return
        
    # Write the pid of the current process (which eventually becomes the target process)
    writePid(name);
        
    # Select application
    if name == 'collector':
        print 'starting collector'
        runCollector(args[2:])
    
        
if __name__ == "__main__":
    sys.exit(main(sys.argv))

