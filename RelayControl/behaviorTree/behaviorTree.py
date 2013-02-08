from twisted.internet import defer, reactor

class __Node(object):
    def execute(self):
        pass

class BlackBoard(object):
    pass

class ParallelNode(__Node):
    def __init__(self, blackboard=None):
        self.children = []
        self.blackboard = blackboard
        
    def execute(self):
        if len(self.children) == 0:
            print 'Parallel needs at least one child'
            return None

        dl = []
        for child in self.children:
            d = child.execute()
            dl.append(d)

        defList = defer.DeferredList(dl, fireOnOneErrback=True, consumeErrors=True)
        
        defList.addCallback(self.parallelCallback)
        defList.addErrback(self.error)
        
        self.d = defer.Deferred()
        return self.d

    def error(self, fail):
        self.d.errback(fail)

    def parallelCallback(self, result):
        print 'parallel callback'
        agg = True
        for _, test in result:
            agg = agg and test
        self.d.callback(agg)
        
    def add(self, child):
        child.blackboard = self.blackboard
        self.children.append(child)
        return self
        
        
class Sequence(__Node):
    def __init__(self, blackboard=None):
        self.children = []
        self.blackboard = blackboard
        self.curChild = 0
        
    def execute(self):
        if not self.children:
            print 'Sequence needs at least one child'
            return None
        
        self.d = defer.Deferred()
        self.moveToNextChild(True)
        return self.d 
    
    
    def error(self, fail):
        print 'Error handler in Sequence node'
        self.d.errback(fail)
    
    def moveToNextChild(self, data):
        if data == True:
            if self.curChild >= len(self.children):
                # Sequence finished with true
                self.d.callback(True)
                return
            
            item = self.children[self.curChild];
            self.curChild += 1
            
            deferFromChild = item.execute()
            if isinstance(deferFromChild, bool):
                self.moveToNextChild(deferFromChild)
            else:
                deferFromChild.addCallback(self.moveToNextChild)
                # deferFromChild.addErrback(self.error)
        else:
            # Sequence finished with false
            self.d.callback(False)
        
        
    def add(self, child):
        child.blackboard = self.blackboard
        self.children.append(child)
        return self

class Selector(__Node):
    def __init__(self, blackboard=None):
        self.children = []
        self.blackboard = blackboard
        self.curChild = 0
        
    def execute(self):
        if not self.children:
            print 'Selector needs at least one child'
            return None

        self.d = defer.Deferred()
        self.moveToNextChild(False)
        return self.d
    
    def error(self, fail):
        print 'Error handler in Selector node'
        self.d.errback(fail)
    
    def moveToNextChild(self, data):
        if data == True:
            self.d.callback(True)
        else:
            if self.curChild >= len(self.children):
                # Select finished with true
                self.d.callback(False)
                return
            
            item = self.children[self.curChild]
            self.curChild = self.curChild + 1
            
            deferFromChild = item.execute()
            if isinstance(deferFromChild, bool):
                self.moveToNextChild(deferFromChild)
            else:           
                deferFromChild.addCallback(self.moveToNextChild)
                deferFromChild.addErrback(self.error)
        
    def add(self, child):
        child.blackboard = self.blackboard
        self.children.append(child)
        return self
    

# Action (Nodes)
class Action(__Node):
    def __init__(self, blackboard=None):
        self.blackboard = blackboard
        
    def execute(self):
        return self.action()

    def action(self):
        d = defer.Deferred()
        print "Dummy - Action Body"
        reactor.callLater(1, d.callback, True)
        return d


# Test program
class NodeA(Action):
    def action(self):
        print 'Action - NodeA'
        d = defer.Deferred()
        reactor.callLater(1, d.callback, True)
        return d
    
class NodeB(Action):
    def action(self):
        print 'Action - NodeB'
        d = defer.Deferred()
        reactor.callLater(1, d.errback, ValueError('error in Node b'))
        return d

def finish(data):
    print 'finish %i' % data
    if reactor.running:
        reactor.stop()

def error(fail):
    print 'Behavior tree failed'
    print str(fail)
    if reactor.running:
        reactor.stop()

if __name__ == '__main__':
    print 'Test behavior trees'
    bb = BlackBoard(); 
    root = ParallelNode(bb)
    
    root.add(NodeB())
    root.add(NodeA())
    
    d = root.execute()
    d.addCallback(finish)
    d.addErrback(error)    
    reactor.run()
    
    
