from relay import RelayService
from select import select
from subprocess import Popen, PIPE
from thrift.protocol import TBinaryProtocol, TBinaryProtocol
from thrift.server import TNonblockingServer, TServer, TProcessPoolServer, \
    TServer
from thrift.transport import TSocket, TTransport, TTwisted
from twisted.internet import reactor
from zope.interface import Interface, implements
import os
import shutil
import string
import tempfile
import zipfile
import time

##########################
## Configuration        ##
PORT = 7900
##########################

def checkEnvironment():
    tmpDir = tempfile.gettempdir()
    if os.path.exists(os.path.join(tmpDir, 'relay')) == False:
        print 'Creating relay directory in tmp...'
        os.mkdir(os.path.join(tmpDir, 'relay')) 
    

class ProcessLoader(object):
    
    VALID_MAINS = ('main', 'main.exe', 'main.py', 'main.sh')
    
    def decompress(self, data, name):
        # Ensure tmp directory is here
        checkEnvironment()
        
        # Create paths
        target = os.path.join(tempfile.gettempdir(), 'relay', name)
        targetFile = os.path.join(tempfile.gettempdir(), 'relay', name + '.zip')
        
        # Write zip file
        print 'writing zip file to disk...'
        targetFileHandle = open(targetFile, 'wb')
        targetFileHandle.write(data)
        targetFileHandle.close()
        
        # Extract zip file
        if os.path.exists(target):
            shutil.rmtree(target, True)
        try:
            print 'mkdir: %s' % (target)
            os.makedirs(target)
        except Exception as e:
            print 'Error while creating target directory'
            return False
        
        zf = zipfile.ZipFile(targetFile)
        for filename in zf.namelist():
            print filename
    
            if filename.endswith('/'):
                try:
                    os.makedirs(os.path.join(target, filename))
                except Exception as e:
                    print 'error while decompressing files %s' % (e)
                    return False
                    
                continue

            # If directory entries are missing (hack)            
            target_dir = filename.split('/')[0:-1]
            if len(target_dir) > 0:
                dir_path = string.join(target_dir, '/')
                os.makedirs(os.path.join(target, dir_path))
            
            try:
                cf = zf.read(filename)
                f = open(os.path.join(target, filename), "wb")
                f.write(cf)
                f.close()
            except Exception as e:
                print 'error unzipping file %s' % (e)
            
        zf.close()
        
        return True
    
    def newProcess(self, name):
        # determine the executable
        mainFile = None
        for main in ProcessLoader.VALID_MAINS:
            target = os.path.join(tempfile.gettempdir(), 'relay', name, main)
            if os.path.exists(target):
                mainFile = main
                break
            
            
        # break if there is no main file
        if mainFile == None:
            print 'missing main file for sensor %s' % (name)
            return None
        
        # determine the executable (python, ..)
        executable = None
        main = None
        try:    
            index = string.rindex(mainFile, '.')
            ending = mainFile[(index + 1):]
            if ending == 'py':
                executable = 'python'
                main = 'main.py'
            elif ending == 'sh':
                executable = 'bash'
                main = 'main.sh'
            elif ending == 'exe':
                executable = None
                main = 'main.exe'
        except ValueError:
            executable = None
            main = None
            return None
        
        # create a new process 
        try:
            path = os.path.join(tempfile.gettempdir(), 'relay', name, main)
            cwd = os.path.join(tempfile.gettempdir(), 'relay', name)
            
            # configure executable and main file
            if executable is None:
                executable = [path, name]
            else:
                executable = [executable, path, name]
            
            process = Popen(executable, stdout=PIPE, bufsize=1, universal_newlines=True, cwd=cwd)
            
            print 'PID %i' % (process.pid)
            return process
        except Exception as e:
            print 'error starting process %s' % (e)
            return None


    def waitFor(self, process):
        process.wait()

    
    def kill(self, process):
        try:
            if process.poll() is None:
                print 'killing the process now...'
                process.kill()
                return True
            return False
        except Exception as e:
            print 'error while killing process %s' % (e)
            return False


class ProcessManager(object):
    def __init__(self):
        self.processLoader = ProcessLoader()
        self.pidMapping = {}
    
    def poll(self, data, name, message):
        # Decompress
        status = self.processLoader.decompress(data, name)
        if status == False:
            print 'Error: Decompression failed'
            return False
           
        base_time = time.time()
        while True: # Restart process if it fails (isAlive polling) 

            # Launch process            
            process = self.processLoader.newProcess(name)
            if process is None:
                print 'Error: Could not launch process'
                return False
            
            while  process.poll() is not None: # Read until message gets found or process is dead (restart necessary)
                if (time.time() - base_time) > 240:
                    print 'ERROR: did not find message within 240 seconds'
                    return False
                
                streams = [process.stdout]
                try:
                    data = select(streams, [], [], 1)[0]
                except: 
                    print 'Error: select failed, restarting process'
                    # Make sure, the process is dead
                    if process.poll() is None:
                        process.kill()
                    continue
            
                for i in range(0, len(data)):
                    line = data[i]
                    line = line.readline()
                    line = line.strip().rstrip()
    
                    if line.find(message) > -1: # Message found
                        # Shutdown the process
                        if process.poll() is None:
                            process.kill()

                        # Return true
                        return True
            
            # Sleep some time between process restarts
            time.sleep(1) 
        
    
    def wait(self, data, name, message, targetFile=None):
        # Decompress
        status = self.processLoader.decompress(data, name)
        if status == False: 
            print 'Error: Decompression failed'
            return False
        
        # Launch process
        process = self.processLoader.newProcess(name)
        if process is None:
            print 'Error: Failed to launch process'
            return False
        
        # Get stream
        streams = []
        if targetFile is None:
            streams = [process.stdout]
        else:
            # Wait launch process to finish 
            process.communicate()
            
            # Hook onto the logfiles
            try:
                print 'Reading from file: %s' % (targetFile)
                stream = open(targetFile, 'r')
                streams = [stream]
            except Exception, e:
                print 'Error: Could not read file %s' % (e)
                return False
        
        # Read the stream until the sequence is found
        import time
        base_time = time.time()        
        while True:
            
            # TODO: Solve this without a hard deadline
            # If the child process finishes .. the polling should stop
            # This requires to start the target process using exec in bash
            if (time.time() - base_time) > 60:
                print 'ERROR: did not find message within 60 seconds'
                return False
            
            data = None
            try:
                data = select(streams, [], [], 1)[0]
            except Exception, e: 
                print 'Error: select failed, %s' % (e)
                return False 
        
            for i in range(0, len(data)):
                line = data[i]
                line = line.readline()
                line = line.strip().rstrip()

                if line.find(message) > -1:
                    print 'message found'
                    return True
                
    
    def launch(self, data, name, wait=True):
        status = self.processLoader.decompress(data, name)
        if status == False:
            print 'Error: Decompression failed'
            return -1
            
        process = self.processLoader.newProcess(name)
        if process is None:
            print 'Error: launching process failed'
            return -1
        
        # Update PID map
        self.pidMapping[process.pid] = process
        
        # Waiting until process is closed?
        if wait:
            print 'waiting for process ...'
            self.processLoader.waitFor(process)
            
            # Update PID map
            del self.pidMapping[process.pid]
            
            # Process is dead
            return 0
        else:
            # TODO: Kill the process after 3 minutes
            pass


        # Return a valid PID            
        return process.pid
    
        
    def isAlive(self, pid):
        if pid not in self.pidMapping:
            print 'Error: no process with PID %i found' % (pid)
            return False
        
        process = self.pidMapping[pid]
        return process.poll() == None
        
        
    def kill(self, pid):
        if pid not in self.pidMapping:
            print 'Error: no process with PID %i found' % (pid)
            return False

        process = self.pidMapping[pid]        
        return self.processLoader.kill(process)
    

class RelayHandler(object):
    implements(RelayService.Iface)
    
    def __init__(self):
        self.processManager = ProcessManager()
    
    def execute(self, code):
        print 'executing python source: %s' % (code)
        context = {
                   'processManager' : self.processManager
                   }
        exec code in context
    
    def __done(self, ret):
        print 'Status: %s' % (ret)
        print 'Waiting for messages...'
    
    def launch(self, binary, name):
        print 'launching drone...'
        ret = self.processManager.launch(binary, name)
        self.__done(ret)
        return ret

    def launchNoWait(self, data, name):
        print 'launching drone... (no wait)'
        ret = self.processManager.launch(data, name, False)
        self.__done(ret)
        return ret
    
    def isAlive(self, pid):
        print 'checking if process %i is alive...' % (pid)
        ret = self.processManager.isAlive(pid)
        self.__done(ret)
        return ret
    
    def kill(self, pid):
        print 'killing process %i...' % (pid)
        ret = self.processManager.kill(pid)
        self.__done(ret)
        return ret
    
    def pollForMessage(self, data, name, message):
        print 'polling for message %s...' % (message)
        ret = self.processManager.poll(data, name, message)
        self.__done(ret)
        return ret
    
    def waitForMessage(self, data, name, message, targetFile):
        print 'polling for message %s in file %s...' % (message, targetFile)
        ret = self.processManager.wait(data, name, message, targetFile)
        self.__done(ret)
        return ret

def main():
    handler = RelayHandler()
    processor = RelayService.Processor(handler)
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    reactor.listenTCP(PORT,
                TTwisted.ThriftServerFactory(processor,
                pfactory), interface="0.0.0.0")
    
    print 'starting reactor on port %i ...' % (PORT)
    reactor.run()

if __name__ == "__main__":
    checkEnvironment()
    main()
