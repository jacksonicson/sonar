from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from relay import *
import build
import time 

PORT = 7900

def main():
    transport = TSocket.TSocket('playdb', 7900)
    transport = TTransport.TFramedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    
    client = RelayService.Client(protocol)
    transport.open()
    
    
    
    
    print "Creating ZIPs"
    build.main()
    
    # Test the execute routine
    str = """for i in range(0,10):
        print 'hello %i' % (i)
    """
    client.execute(str)

    # Read contents of the zip file
    file = open('spec_dbload.zip', 'rb')
    data = file.read()
    file.close()
    
    # Launch the ZIP file
#    res = client.launch(data, "test")
#    print res
    
    pid = client.launchNoWait(data, "test")
    print 'pid is %i' % (pid)
    
    while True:
        sta = client.isAlive(pid)
        print 'alive %i' % (sta)
        time.sleep(1)
    


if __name__ == '__main__':
    main()