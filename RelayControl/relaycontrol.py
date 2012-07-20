from relay import *
from thrift import Thrift, Thrift
from thrift.protocol import TBinaryProtocol, TBinaryProtocol
from thrift.transport import TSocket, TTransport, TTwisted
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.internet.protocol import ClientCreator
from twisted.internet import defer
PORT = 7900

def done(done):
    print "DOEN"




@inlineCallbacks
def test(client):
    print 'client'
    
    d1 = client.execute("print 'hello'").addCallback(done)
    print 'stop'

    d = defer.Deferred()
    
    yield d1
    
    print "final"


def te2(client):
    print "one deferr fired"


def done_all(done):
    print "ALL METHOD EXECUTED SUCCESSFULLY %i" % (len(done))
    for res in done:
        print res
        
    reactor.stop()

def te(client_list):
    print "all connections established %s" % (client_list)
    
    li = []
    for status in client_list:
        de = defer.Deferred()
        li.append(de)
        d = status[1].execute("print 'hello'").addCallback(de.callback)
        
    dl = defer.DeferredList(li)
    dl.addCallback(done_all)
        
    print 'done'

def main():
    
    ports = [PORT, PORT+1]
    
    items = []
    for i in ports:
        print 'Starting client for host %s:%i ' % ('127.0.0.1', i)
        
        d = ClientCreator(reactor,
                          TTwisted.ThriftClientProtocol,
                          RelayService.Client,
                          TBinaryProtocol.TBinaryProtocolFactory(),
                          ).connectTCP("127.0.0.1", i)
        d.addCallback(lambda conn: conn.client)
        
        myDef = defer.Deferred()
        items.append(myDef)
        d.addCallback(myDef.callback)


    wa = defer.DeferredList(items)
    wa.addCallback(te)

    print 'Starting reactor...'
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
