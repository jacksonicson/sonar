from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from relay import *
import build
import time 

PORT = 7900


from twisted.internet.defer import inlineCallbacks
from twisted.internet import reactor
from twisted.internet.protocol import ClientCreator

from thrift import Thrift
from thrift.transport import TTwisted
from thrift.protocol import TBinaryProtocol

def done(done):
    print "DOEN"

@inlineCallbacks
def test(client):
    print 'client'
    
    d1 = client.execute("test").addCallback(done)
    print 'stop'
    
    yield d1
    
    print "final"
        
    


def main():
    
    for i in range(0,5):
        d = ClientCreator(reactor,
                          TTwisted.ThriftClientProtocol,
                          RelayService.Client,
                          TBinaryProtocol.TBinaryProtocolFactory(),
                          ).connectTCP("127.0.0.1", 9091)
        d.addCallback(lambda conn: conn.client)
        d.addCallback(test)

    print 'running'
    reactor.run()
    
#    transport = TSocket.TSocket('playdb', 7900)
#    transport = TTransport.TFramedTransport(transport)
#    protocol = TBinaryProtocol.TBinaryProtocol(transport)
#    
#    client = RelayService.Client(protocol)
#    transport.open()
#    
#    
#    
#    
#    print "Creating ZIPs"
#    build.main()
#    
#    # Test the execute routine
#    str = """for i in range(0,10):
#        print 'hello %i' % (i)
#    """
#    client.execute(str)
#
#    # Read contents of the zip file
#    file = open('spec_dbload.zip', 'rb')
#    data = file.read()
#    file.close()
#    
#    # Launch the ZIP file
##    res = client.launch(data, "test")
##    print res
#    
#    pid = client.launchNoWait(data, "test")
#    print 'pid is %i' % (pid)
#    
#    while True:
#        sta = client.isAlive(pid)
#        print 'alive %i' % (sta)
#        time.sleep(1)
    


if __name__ == '__main__':
    main()