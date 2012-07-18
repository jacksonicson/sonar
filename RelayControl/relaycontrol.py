from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from relay import *

def main():
    transport = TSocket.TSocket('localhost', 9191)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = RelayService.Client(protocol)
    transport.open()
    
    # Test the execute routine
    client.execute('print "hello world"')
    
    
    file = open('test.zip', 'rb')
    data = file.read()
    file.close()
    
    res = client.launch(data, "test")
    print res
    
    pid = client.launchNoWait(data, "test")
    print 'pid is %i' % (pid)
    
    res = client.kill(pid)
    print res
    


if __name__ == '__main__':
    main()