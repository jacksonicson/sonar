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
from threading import Thread
import thread

##########################
## Configuration        ##
PORT = 7900
MAX_WAIT_TIME = 230
##########################

def checkEnvironment():
    tmpDir = tempfile.gettempdir()
    if os.path.exists(os.path.join(tmpDir, 'relay')) == False:
        print 'Creating relay directory in tmp...'
        os.mkdir(os.path.join(tmpDir, 'relay')) 
    

class ProcessLoader(Thread):
    
    VALID_MAINS = ('main', 'main.exe', 'main.py', 'main.sh')
    
    def __init__(self):
        super(ProcessLoader, self).__init__()
        
        # Alive flag
        self.alive = True
        
        # Lock
        self.lock = thread.allocate_lock()
        
        # Watch list
        self.watching = []
        
        self.start()
        print 'forged: process loader'
    
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
            
            process = Popen(executable, stdout=PIPE, bufsize=0, universal_newlines=True, cwd=cwd)
            
            print 'PID %i' % (process.pid)
            return process
        except Exception as e:
            print 'error starting process %s' % (e)
            return None

    def attach(self, process):
        self.lock.acquire()
        self.watching.append(process)
        self.lock.release()

    def run(self):
        while self.alive:
            
            self.lock.acquire()
            # Update streams list
            streams = []
            _watching = []
            for process in self.watching:
                # Cleans up dead processes
                print 'check'
                if process.poll() is None: 
                    streams.append(process.stdout)
                    _watching.append(process)
            self.watching = _watching                
            self.lock.release()
            
            # print 'cycle %i' % len(streams)
            if len(streams) == 0:
                time.sleep(3)
                continue
            
            # Wait for receive and pick the stdout list
            try:
                data = select(streams, [], [], 3)[0]
            except: 
                print 'stopping continuouse because of error in select'
                break 
            
            # Data is not stored
            for i in range(0, len(data)):
                line = data[i]
                line = line.readline()
                line = line.strip().rstrip()
                print line 
            

    def shutdown(self):
        # Exit main loop 
        self.alive = False
        
        # Wait until main loop is closing and taking all the processes with it
        while self.isAlive():
            self.join(timeout=3)
            print 'waiting for: process loader'
            
        print 'joined: process loader'


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
    implements(RelayService.Iface)
    
    def __init__(self):
        self.processLoader = ProcessLoader()
        self.pidMapping = {}
    

    def __launch(self, data, name):
        # Decompress
        status = self.processLoader.decompress(data, name)
        if status == False: 
            print 'Error: Decompression failed'
            return None
        
        # Launch process
        process = self.processLoader.newProcess(name)
        if process is None:
            print 'Error: Failed to launch process'
            return None
        
        return process

    '''
    Starts and restarts a process to find a message in its stdout stream.
    The process is terminated as soon as the message gets found or a timeout occurs.     
    '''
    def pollForMessage(self, data, name, message):
        print 'poll for message...'
        
        # Decompress
        status = self.processLoader.decompress(data, name)
        if status == False:
            print 'Error: Decompression failed'
            return False
           
        base_time = time.time()
        for _ in xrange(0, 20): # Restart process if it fails
            # Launch process
            print 'Launching process...'            
            process = self.processLoader.newProcess(name)
            if process is None:
                print 'Error: Could not launch process'
                return False
            
            # Read on the active process until message gets found
            # This loop exists if the process dies or the message gets found
            while  process.poll() is None:
                # Impose a waiting time limit  
                if (time.time() - base_time) > MAX_WAIT_TIME:
                    print 'ERROR: did not find message within %i seconds' % MAX_WAIT_TIME
                    # Shutdown the process
                    if process.poll() is None:
                        process.kill()
                    return False
                
                try:
                    streams = [process.stdout]
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
                        print 'Message found...'
                        
                        # Shutdown the process
                        if process.poll() is None:
                            process.kill()

                        # Return true
                        return True
            
            # Sleep some time between process restarts
            time.sleep(15)
        
        # Process was restarted too often
        print 'Error: process was restarted too often'
        return False

    def waitForMessage(self, data, name, message, targetFile):
        print 'wait for message...'
        
        # Start process
        process = self.__launch(data, name)
        if process == None: return False
        
        # Get stream from process or target file if set
        if targetFile is None:
            streams = [process.stdout]
        else:
            # Wait launch process to finish 
            process.communicate()
            
            # Hook onto the target file
            try:
                print 'Reading from file: %s' % (targetFile)
                stream = open(targetFile, 'r')
                streams = [stream]
            except Exception, e:
                print 'Error: Could not read file %s' % (e)
                return False
        
        # Read the stream until the sequence is found
        base_time = time.time()        
        while True:
            if (time.time() - base_time) > MAX_WAIT_TIME:
                print 'ERROR: did not find message within %i seconds' % MAX_WAIT_TIME
                return False
            
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
                    
                    # handover stdout control
                    self.processLoader.attach(process)
                    
                    return True
                
    
    def _launch(self, data, name, wait=True):
        # Start process
        process = self.__launch(data, name)
        if process == None: return False
        
        # Update PID map
        self.pidMapping[process.pid] = process
        
        # Waiting until process is closed?
        if wait:
            print 'waiting for process ...'
            process.wait()
            print 'done'
            
            # Update PID map
            del self.pidMapping[process.pid]
            
            # Process is dead
            print 'returned'
            return 0
        else:
            # handover stdout control
            self.processLoader.attach(process)
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
    

    def execute(self, code):
        print 'executing python source: %s' % (code)
        context = {
                   'processManager' : self.processManager
                   }
        exec code in context
    
    def launch(self, data, name):
        return self._launch(data, name, True)
    
    def launchNoWait(self, data, name):
        return self._launch(data, name, False)

    def shutdown(self):
        self.processLoader.shutdown()



def main():
    handler = ProcessManager()
    processor = RelayService.Processor(handler)
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    reactor.listenTCP(PORT,
                TTwisted.ThriftServerFactory(processor,
                pfactory), interface="0.0.0.0")
    
    print 'starting reactor on port %i ...' % (PORT)
    reactor.run()
    
    print 'stopping threads'
    handler.shutdown()


if __name__ == "__main__":
    checkEnvironment()
    main()
