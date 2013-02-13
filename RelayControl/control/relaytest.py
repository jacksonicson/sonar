import drones, hosts, base
from twisted.internet import defer, reactor

def finished():
    reactor.stop()

def test5_res(res, client_list):
    print 'test5: %s' % res
    res = res[0]
    assert(res[0] == True)
    assert(res[1] == True)
    finished()


def test5_alive(res, client_list):
    dlist = []
    pid = res[0][1]
    for host in hosts.get_hosts('action'):
        print 'launch test3   %s' % (host)
        
        d = base.client(client_list, host).isAlive(pid)
        dlist.append(d)
        
    dl = defer.DeferredList(dlist)  
    dl.addCallback(test5_res, client_list)

def test5(client_list):
    dlist = []
    
    for host in hosts.get_hosts('action'):
        print 'launch test3   %s' % (host)
        
        d = base.launch(client_list, host, 'test', wait=False)
        dlist.append(d)
        
    dl = defer.DeferredList(dlist)  
    dl.addCallback(test5_alive, client_list)


def test4_res(res, client_list):
    print 'test4: %s' % res
    res = res[0]
    assert(res[0] == True)
    assert(res[1] == True)
    test5(client_list)
    

def test4(client_list):
    dlist = []
    
    for host in hosts.get_hosts('action'):
        print 'launch test3   %s' % (host)
        
        d = base.wait_for_message(client_list, host, 'test', 'done', '/tmp/testfile')
        dlist.append(d)
    
    dl = defer.DeferredList(dlist)  
    dl.addCallback(test4_res, client_list)


def test3_res(res, client_list):
    print 'test3: %s' % res
    res = res[0]
    assert(res[0] == True)
    assert(res[1] == True)
    test4(client_list)

def test3(client_list):
    dlist = []
    
    for host in hosts.get_hosts('action'):
        print 'launch test3   %s' % (host)
        
        d = base.wait_for_message(client_list, host, 'test', 'done')
        dlist.append(d)
    
    dl = defer.DeferredList(dlist)  
    dl.addCallback(test3_res, client_list)
    

def test2_res(res, client_list):
    print 'test2: %s' % res
    res = res[0]
    assert(res[0] == True)
    assert(res[1] == True)
    test3(client_list)

def test2(client_list):
    dlist = []
    
    for host in hosts.get_hosts('action'):
        print 'launch test2   %s' % (host)
        
        d  = base.poll_for_message(client_list, host, 'test', 'done')
        dlist.append(d)
        
    dl = defer.DeferredList(dlist)  
    dl.addCallback(test2_res, client_list)


def test1_res(res, client_list):
    print 'test1: %s' % res
    res = res[0]
    assert(res[0] == True)
    assert(res[1] == 0)
    test2(client_list)

def test1(client_list):
    dlist = []
    
    for host in hosts.get_hosts('action'):
        print 'launch test1   %s' % (host)
        
        d = base.launch(client_list, host, 'test', wait=True)
        dlist.append(d)

    dl = defer.DeferredList(dlist)  
    dl.addCallback(test1_res, client_list)


def test0_res(res, client_list):
    print 'test0: %s' % res
    res = res[0]
    assert(res[0] == True)
    assert(res[1] > 0)
    test1(client_list)
    
def test0(client_list):
    dlist = []
    for host in hosts.get_hosts('action'):
        print 'launch test0   %s' % (host)
        
        d = base.launch(client_list, host, 'test', wait=False)
        dlist.append(d)
    
    dl = defer.DeferredList(dlist)  
    dl.addCallback(test0_res, client_list)
    
    
def main():
    # Create drones
    drones.main()
    
    # Add hosts
    hosts.add_host('192.168.96.6', 'action')
        
    hosts_map = hosts.get_hosts_list()
    
    # Connect with all drone relays
    deferList = base.connect(hosts_map)
    wait = defer.DeferredList(deferList)
    
    # Decide what to do after connection setup
    wait.addCallback(test0)
    
    # Start the Twisted reactor
    reactor.run()

if __name__ == '__main__':
    main()
