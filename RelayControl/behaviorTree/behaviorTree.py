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
        reactor.callLater(4, d.callback, False)
        return d

class Action2(Action):
    
    def action(self):
        d = defer.Deferred()
        print "Executing Actio2n"
        reactor.callLater(4, d.callback, False)
        return d

class Action3(Action):
    
    def action(self):
        d = defer.Deferred()
        print "Executing Actio3n"
        reactor.callLater(4, d.callback, True)
        return d

def stop(data):
    print "Stop method"
    print data
    reactor.stop()

b = BlackBoard()
s = Sequence(b).addChild(Action3(b)).addChild(Action3(b))
s2 = Selector(b).addChild(Action(b)).addChild(Action2(b)).addChild(s)
#s2 = Selector(b).addChild(Action(b)).addChild(Action(b)).addChild(s)
d = s2.execute()     
d.addCallback(stop)

reactor.run()
print b.getData("hi")
