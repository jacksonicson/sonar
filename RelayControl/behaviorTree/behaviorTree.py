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

        defList = defer.DeferredList(dl, consumeErrors=0)
        defList.addCallback(self.parallelCallback)
        self.d = defer.Deferred()
        return self.d

    def parallelCallback(self, result):
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
def finish(data):
    print 'finish %i' % data
    if reactor.running:
        reactor.stop()

if __name__ == '__main__':
    print 'Test behavior trees'
    bb = BlackBoard(); 
    root = Sequence(bb)
    root.add(Action())
    root.add(Action())
    
    d = root.execute()
    d.addCallback(finish)    
    reactor.run()
    
    
