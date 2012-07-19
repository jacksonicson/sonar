from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from relay import *

PORT = 7900

def main():
    transport = TSocket.TSocket('playground', 7900)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = RelayService.Client(protocol)
    transport.open()
    
    # Test the execute routine
    str = """for i in range(0,10):
        print 'hello %i' % (i)
    """
    client.execute(str)

    # Read contents of the zip file    
    file = open('test.zip', 'rb')
    data = file.read()
    file.close()
    
    # Launch the ZIP file
    res = client.launch(data, "test")
    print res
    
    pid = client.launchNoWait(data, "test")
    print 'pid is %i' % (pid)
    
    res = client.kill(pid)
    print res
    


if __name__ == '__main__':
    main()