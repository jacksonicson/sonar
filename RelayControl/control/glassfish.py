'''
This module checks if all Glassfish servers are running
and if the SPECjEnterprise2010 application is running
'''
from twisted.internet import reactor
from twisted.web.client import Agent
from twisted.web.http_headers import Headers
from twisted.internet.protocol import Protocol
from twisted.internet.defer import Deferred
from twisted.internet import defer

class BeginningPrinter(Protocol):
    def __init__(self, finished):
        self.finished = finished
        self.remaining = 1024 * 10

    def dataReceived(self, bytes):
        if self.remaining:
            display = bytes[:self.remaining]
            print display
            self.remaining -= len(display)

    def connectionLost(self, reason):
        print 'Finished receiving body:', reason.getErrorMessage()
        self.finished.callback(None)

def main(targets):
    agent = Agent(reactor)

    dlist = []
    for name in targets:
        d = agent.request(
                          'GET',
                          'http://%s:8080/specj/' % name,
                          Headers({'User-Agent': ['Twisted Web Client Example']}),
                          None)
        d.addCallback(cbResponse, name)
        dlist.append(d)
        
    wait = defer.DeferredList(dlist)
        
    return wait
    
failed = []    
def cbResponse(ignored, target):
    if ignored.code == 200:
        print 'OK: %s' % target
    else:
        print 'FAIL: %s' % target
        failed.append(target)

def cbShutdown(ignored):
    print 'done'
    reactor.stop()
 
def _status(ignored):
    if len(failed) == 0:
        print 'SUCCESSFUL'
    else:
        print 'FAILED'        
    

if __name__ == '__main__':
    targets = []
    for i in xrange(0,18):
        targets.append('target%i' % i)
    wait = main(targets)
    wait.addBoth(cbShutdown)
    wait.addCallback(_status)
    reactor.run()