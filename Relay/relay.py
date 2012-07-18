from relay import *
from thrift.protocol import TBinaryProtocol
from thrift.server import TNonblockingServer, TServer
from thrift.transport import TSocket, TTransport

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
    
    handler = CalculatorHandler()
    processor = Calculator.Processor(handler)
    transport = TSocket.TServerSocket(port=9191)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    
    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
    
    server.serve()
    

if __name__ == "__main__":
    main()
