from twisted.internet import defer, reactor

# The Node 
class __Node(object):
    def execute(self):
        pass

"""The Blackboard class which consists of a dictionary to store temporary data
in a key-value pair format"""
class BlackBoard:
    def __init__(self):
        self.data = {}
        pass

    def addData(self, key, value):
        self.data[key] = value

    def getData(self, key):
        try:
            return self.data[key]
        except:
            pass

# Parallel Node
class ParallelNode(__Node):
    def __init__(self, blackboard):
        self.children = []
        self.deferreds = []

    def execute(self):
        if len(self.children) == 0:
            print "Nodes should have at least one action"
            return None

        self.d = defer.Deferred()
        print "Execute in Parallel"
        for child in self.children:
            d = child.execute()
            self.deferreds.append(d)

        defList = defer.DeferredList(self.deferreds, consumeErrors=0)
        defList.addCallback(self.parallelCallback)
        return d

    def parallelCallback(self, result):
        print "Callback in result"
        for ignore, data in result:
            print data
        self.d.callback(result)
        
    def addChild(self, child):
        self.children.append(child)
        return self
        
# Sequence
class Sequence(__Node):
    def __init__(self, blackboard):
        self.children = []
        self.blackboard = blackboard
        self.curChild = 0
        
    def execute(self):
        if len(self.children) == 0:
            print "Sequence should have at least one action"
            return None

        print "Execute in Sequence"
        self.d = defer.Deferred()
        self.moveToNextChild(True)
        return self.d
    
    def moveToNextChild(self, data):
        if(self.curChild == len(self.children)):
            print "Going to callback parent now"
            self.d.callback(data)
            pass
        
        if data == True:
            item = self.children[self.curChild];
            self.curChild = self.curChild + 1
            deferFromChild = item.execute()
            deferFromChild.addCallback(self.moveToNextChild)
        else :
            self.d.callback(data)
            pass
        
    def addChild(self, child):
        self.children.append(child)
        return self

# Selector
class Selector(__Node):
    def __init__(self, blackboard):
        self.children = []
        self.blackboard = blackboard
        self.curChild = 0
        
    def execute(self):
        if len(self.children) == 0:
            print "Selector should have at least one action"
            return None

        print "Execute in Selector"
        self.d = defer.Deferred()
        self.moveToNextChild(False)
        return self.d
    
    def moveToNextChild(self, data):
        if(self.curChild == len(self.children)):
            print "Going to callback parent now"
            self.d.callback(data)
            pass
        
        if data == True:
             self.d.callback(data)
        else :
            item = self.children[self.curChild];
            self.curChild = self.curChild + 1
            deferFromChild = item.execute()
            deferFromChild.addCallback(self.moveToNextChild)
            pass
        
    def addChild(self, child):
        self.children.append(child)
        return self
    

# Action (Nodes)
class Action(__Node):
    def __init__(self, blackboard):
        self.blackboard = blackboard
        
    def execute(self):
        self.d = defer.Deferred()
        defir = self.action()
        defir.addCallback(self.d.callback)
        return self.d

    def action(self):
        d = defer.Deferred()
        print "Executing Action"
        reactor.callLater(4, d.callback, True)
        return d


###################################################################
# TEST PROGRAMS
###################################################################

class Action2(Action):
    
    def action(self):
        d = defer.Deferred()
        print "Executing Actio2n"
        self.blackboard.addData("test", "val")
        reactor.callLater(4, d.callback, False)
        return d

class Action3(Action):
    
    def action(self):
        d = defer.Deferred()
        print "Executing Actio3n"
        self.blackboard.addData("test", "val2")
        reactor.callLater(4, d.callback, True)
        return d
