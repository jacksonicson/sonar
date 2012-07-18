from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from thrift.server import TNonblockingServer
from relay import *

# sys.path.append('../gen-py')

class RelayHandler(object):
    def __init__(self):
        pass
    
    
    def execute(self, code):
        print 'executing'
        pass
    
    def getPids(self):
        pass
    
    def kill(self, pid):
        pass
    
    
def main():
    print 'ok'
    
    handler = RelayHandler()
    
    processor = RelayService.Processor(handler)
    transport = TSocket.TServerSocket(port=9191)
    
    # tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    
    
    server = TNonblockingServer.TNonblockingServer(processor,  transport)
    
    server.serve()
    

if __name__ == "__main__":
    main()