from relay import RelayService
from subprocess import Popen, PIPE
from thrift.protocol import TBinaryProtocol
from thrift.server import TNonblockingServer, TServer
from thrift.transport import TSocket, TTransport
import os
import shutil
import string
import tempfile
import zipfile


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
            
            # configure executable and main file
            if executable is None:
                executable = [path, name]
            else:
                executable = [executable, path, name]
            
            process = Popen(executable, stdout=PIPE, bufsize=1, universal_newlines=True)
            
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
                process.kill()
            return True
        except Exception as e:
            print 'error while killing process %s' % (e)
            return False


class ProcessManager(object):
    def __init__(self):
        self.processLoader = ProcessLoader()
        self.pidMapping = {}
    
    def launch(self, data, name, wait=True):
        status = self.processLoader.decompress(data, name)
        if status == True:
            print 'Decomression successful'
            
        print 'Launching...'
        process = self.processLoader.newProcess(name)
        if process is None:
            print 'Error while launching process'
            return -1
        else:
            self.pidMapping[process.pid] = process
        
        if wait:
            print 'Waiting..'
            self.processLoader.waitFor(process)
            print 'Finished'
            del self.pidMapping[process.pid]
            
        return process.pid
        
    def kill(self, pid):
        if pid not in self.pidMapping:
            print 'No process with the given pid %i found' % (pid)
            return False

        process = self.pidMapping[pid]        
        return self.processLoader.kill(process)
    

class RelayHandler(object):
    
    def __init__(self):
        self.processManager = ProcessManager()
    
    def execute(self, code):
        print 'executing %s' % (code)
        context = {
                   'processManager' : self.processManager
                   }
        exec code in context
    
    def launch(self, binary, name):
        print 'launching package'
        self.processManager.launch(binary, name)
        return 0

    def launchNoWait(self, data, name):
        print 'Launching package without waiting for it!'
        pid = self.processManager.launch(data, name, False)
        return pid    
    
    def kill(self, pid):
        return self.processManager.kill(pid)
    
PORT = 7900
    
def main():
    handler = RelayHandler()
    processor = RelayService.Processor(handler)
    transport = TSocket.TServerSocket(port=PORT)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    
    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)

    print 'Listening on port %i' % (PORT)    
    server.serve()
    

if __name__ == "__main__":
    main()
