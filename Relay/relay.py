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

PORT = 7900


def checkEnvironment():
    tmpDir = tempfile.gettempdir()
    if os.path.exists(os.path.join(tmpDir, 'relay')) == False:
        print 'Creating relay directory in tmp...'
        os.mkdir(os.path.join(tmpDir, 'relay')) 
    

class ProcessLoader(object):
    
    VALID_MAINS = ('main', 'main.exe', 'main.py', 'main.sh')
    
    def decompress(self, data, name):
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
        for info in zf.infolist():
            print info.filename
    
            if info.filename.endswith('/'):
                try:
                    os.makedirs(os.path.join(target, info.filename))
                except Exception as e:
                    print 'error while decompressing files %s' % (e)
                    return False
                    
                continue
            
            cf = zf.read(info.filename)
            f = open(os.path.join(target, info.filename), "wb")
            f.write(cf)
            f.close()
            
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
            
            process = Popen(executable, stdout=PIPE, bufsize=10, universal_newlines=True, cwd=cwd)
            
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
           
        # Restart process if it fails (isAlive polling)
        while True: 

            # Launch process            
            process = self.processLoader.newProcess(name)
            if process is None:
                print 'Error: Could not launch process'
                return False
            
            # Read until message gets found or process is dead (restart necessary)
            while True:
                streams = [process.stdout]
                data = None
                try:
                    data = select(streams, [], [], 1)[0]
                except: 
                    print 'Error: select failed, restarting process'
                    
                    # Kill the process (just to be sure)
                    if process.poll() is None:
                        process.kill()
                    
                    break 
            
                for i in range(0, len(data)):
                    line = data[i]
                    line = line.readline()
                    line = line.strip().rstrip()
    
                    if line.find(message) > -1:
                        # This process is still alive (no return code)
                        if process.poll() is None:
                            process.kill()

                        # Return
                        return True
            
                # Process is dead
                if process.poll() is not None:
                    break
                    
            # Sleep some time between the iterations
            import time
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
        
        # Read the stream until the sequence is found        
        while True:
            
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
    
    def launch(self, binary, name):
        print 'launching drone...'
        return self.processManager.launch(binary, name)

    def launchNoWait(self, data, name):
        print 'launching drone... (no wait)'
        return self.processManager.launch(data, name, False)
    
    def isAlive(self, pid):
        print 'checking if process %i is alive...' % (pid)
        return self.processManager.isAlive(pid)
    
    def kill(self, pid):
        print 'killing process %i...' % (pid)
        return self.processManager.kill(pid)
    
    def pollForMessage(self, data, name, message):
        print 'polling for message %s...' % (message)
        return self.processManager.poll(data, name, message)
    
    def waitForMessage(self, data, name, message, targetFile):
        print 'polling for message %s in file %s...' % (message, targetFile)
        return self.processManager.wait(data, name, message, targetFile)

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
