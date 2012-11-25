from heapq import heapify, heappop
from sets import Set
import sys

class pq(object):
    def __init__(self, init=None):
        self.inner, self.item_f = [], {}
        if not None is init:
            self.inner = [[priority, item] for item, priority in enumerate(init)]
            heapify(self.inner)
            self.item_f = {pi[1]: pi for pi in self.inner}

    def __contains__(self, item):
        return item in self.item_f

    def put(self, item, priority):
        entry = [priority, item]
        self.inner.append(entry)
        heapify(self.inner)
        self.item_f[item] = entry

    def top_one(self):
        if not len(self.inner): return None
        priority, item = heappop(self.inner)
        del self.item_f[item]
        return item

    def re_prioritize(self, items, prioritizer): # =lambda x: x + 1
        for item in items:
            if not item in self.item_f: continue
            entry = self.item_f[item]
            entry[0] = prioritizer(entry[0])
        heapify(self.inner)

class ANode(object):
    def __init__(self, nodes=None, domains=None):
        self.predecessor = None
        self.g = 99999
        
        self.nodes = nodes
        self.domains = domains
     
    def dump(self):
        print self.nodes
        print self.domains
        
    def get_successors(self, mesh):
        # generates _all_ successors
        # The heuristic will not go into all of them
        
        # for all migration possibilities create a new state
        # state heuristics is determined by f_heuristics function 
        
        successors = []
        costs = []
        
        # each domain to each node except its own 
        for d in xrange(len(self.domains)): 
            for node in xrange(len(self.nodes)): 
                nodes = list(self.nodes)
                domains = list(self.domains)
                
                if domains[d] == node:
                    continue
                
                domains[d] = node
                new = ANode(nodes, domains)
                # check if node is in mesh already
                test = mesh.find(new)
                if test:
                    new = test
                else:
                    new.predecessor = self
                    mesh.put(new)
                    
                successors.append(new)
                costs.append(1)
        
        return (successors, costs)
       
    def __eq__(self, another):
        return self.domains == another.domains
    
    def __hash__(self):
        h = 0
        for i, v in enumerate(self.domains):
            h += (i+1) * v
        return h
        
    def f_heuristics(self, target):
        counter = 0
        for i in xrange(len(self.domains)):
            if target.domains[i] != self.domains[i]:
                counter += 1
                
        return counter
        


class AStar(object):
    def __init__(self):
        self.openlist = pq()
        self.closelist = Set()
    
    def search(self, mesh, start, end):
        self.mesh = mesh
        self.end = end
        
        # Add start node to the open list
        start.g = 0
        self.openlist.put(start, 0)
        
        try:
            while True:
                # sys.stdout.write('.') 
                value = self.openlist.top_one()
                if value is None:
                    print 'nothing found again'
                    return
                
                if value == end:
                    print 'END FOUND.... run backtracking now'
                    return end
                
                self.expand(value)
                self.closelist.add(value)  
                
        except KeyError:
            pass
                    
        print 'nothing found'
        
    
    def expand(self, current):
        successors, costs = current.get_successors(self.mesh)
        for i in xrange(len(successors)):
            successor = successors[i] 
            if successor in self.closelist:
                continue
            
            # Relaxion on costs
            new_g = current.g + costs[i]
            # TODO1
            if successor in self.openlist and new_g >= successor.g:
                continue
            
            # Update predecessor for backtracking
            successor.predecessor = current
            successor.g = new_g
            
            # Update open list
            f = new_g + current.f_heuristics(self.end)
            if successor in self.openlist:
                self.openlist.re_prioritize((successor,), lambda x: f)
            else:
                self.openlist.put(successor, f) 

def main():
    # Create initial state
    nodes = [0 for _ in xrange(0, 3)]
    domains = [0 for _ in xrange(0, 10)]
    node_index = 0
    for d in xrange(0, 10):
        domains[d] = node_index
        node_index = (node_index + 1) % len(nodes)
        
    # Create target state
    target = list(domains)
#    target[0] = 2

    target[1] = 2
    target[3] = 1
    target[4] = 2
        
    # Create target and end node
    start = ANode(nodes, domains)
    target = ANode(nodes, target)
    
    print start.domains
    
    # Create a new mesh
    mesh = Mesh()
    mesh.put(start)
    mesh.put(target)
    
    # Run search
    s = AStar()
    end = s.search(mesh, start, target)
    while True:
        print end.domains
        if end.predecessor is None:
            break
        end = end.predecessor

class Mesh(object):
    def __init__(self):
        self.dict = {}
     
    def dump(self):
        print self.dict
        
    def find(self, node):
        if self.dict.has_key(node):
            return self.dict[node]
        return None
    
    def put(self, node):
        if self.find(node) is None:
            self.dict[node] = node

def testNode():
    # Create initial state
    nodes = [0 for _ in xrange(3)] # the load of a node
    domains = [0 for _ in xrange(10)] # domain - node mapping
    
    node_index = 0
    for d in xrange(0, 10):
        domains[d] = node_index
        node_index = (node_index + 1) % len(nodes)
        
    # Create target and end node
    start = ANode(nodes, domains)
    
    nodes = list(nodes)
    domains = list(domains)
    domains[0] = 4
    end = ANode(nodes, domains)
    print start == end
    
    print 'hahses'
    print end.__hash__()
    print start.__hash__()

    test = {}
    test[end] = 'asdf'
    test[start] = 'super'
    print test[end]
    
    print 'in test'
    print start in test
    
    print 'test pq'
    q = pq()
    q.put(start, 1)
    q.put(end, 0)
    print q.top_one() == end
    q.put(end, 0)
    print q.top_one() == end
    print q.top_one() == start
    
    print 'test successors'
    mesh = Mesh()
    s, c = start.get_successors(mesh)
    print len(s) 
#    for i in s:
#        print i.domains  

if __name__ == '__main__':
    testNode()
    main()
    
        
        
    
