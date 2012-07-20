from relay import *
from thrift import Thrift, Thrift
from thrift.protocol import TBinaryProtocol, TBinaryProtocol
from thrift.transport import TSocket, TTransport, TTwisted
from twisted.internet import defer, reactor
from twisted.internet.defer import inlineCallbacks
from twisted.internet.protocol import ClientCreator
import build
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


def start_rain(ret, client_list):
    print 'Starting rain now...'
    
    # Reading packages
    file = open('rain_start.zip', 'rb')
    file_rain_start = file.read()
    file.close()

    dp = defer.Deferred()
    client_list[0][1].launch(file_rain_start, "rain_start").addCallback(dp.callback)
    
    dl = defer.DeferredList([dp])
    dl.addCallback(done_all)


def shutdown_glassfish(client_list):
    print "shutting down system... %s" % (client_list)
    
    # Reading packages
    file = open('glassfish_stop.zip', 'rb')
    file_glassfish_stop = file.read()
    file.close()
    
    # Launch packages on hosts
    dp = defer.Deferred()
    client_list[0][1].launch(file_glassfish_stop, "glassfish_stop").addCallback(dp.callback)
    
    dl = defer.DeferredList([dp])
    dl.addCallback(done_all)
    

def start_glassfish_database(client_list):
    print "all connections established %s" % (client_list)

    # Reading packages
    file = open('glassfish_start.zip', 'rb')
    file_glassfish_start = file.read()
    file.close()
    
    file = open('spec_dbload.zip', 'rb')
    file_spec_dbload = file.read()
    file.close() 

    # Launch packages on hosts
    dp = defer.Deferred()
    client_list[0][1].launchNoWait(file_glassfish_start, "glassfish_start").addCallback(dp.callback)
    
    dd = defer.Deferred()
    client_list[1][1].launch(file_spec_dbload, "spec_dbload").addCallback(dd.callback)

    dl = defer.DeferredList([dp, dd])
    dl.addCallback(start_rain, client_list)
    

def main():
    
    build.main()
    
    hosts = ['playground', 'playdb']
    
    items = []
    for i in hosts:
        print 'Starting client for host %s:%i ' % (i, PORT)
        
        d = ClientCreator(reactor,
                          TTwisted.ThriftClientProtocol,
                          RelayService.Client,
                          TBinaryProtocol.TBinaryProtocolFactory(),
                          ).connectTCP(i, PORT)
        d.addCallback(lambda conn: conn.client)
        
        myDef = defer.Deferred()
        items.append(myDef)
        d.addCallback(myDef.callback)


    wa = defer.DeferredList(items)
    
    wa.addCallback(start_glassfish_database)
    #wa.addCallback(shutdown_glassfish)

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
#    
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
