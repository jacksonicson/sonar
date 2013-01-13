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

    def put(self, item, priority, heap=True):
        entry = [priority, item]
        self.inner.append(entry)
        if heap:
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
    
    def heap(self):
        heapify(self.inner)

class ANode(object):
    def __init__(self, nodeload, domains, domainload):
        self.predecessor = None
        self.g = 99999
        
        self.nodeload = nodeload
        self.domainload = domainload
        self.domains = domains
        
        self.successors = None
        self.costs = None
        
        self.hash = None
        self.tmp = None
     
    def dump(self):
        print self.nodes
        print self.domains
        
        
    def get_successors(self, mesh, target):
        # generates _all_ successors
        # The heuristic will not go into all of them
        
        # for all migration possibilities create a new state
        # state heuristics is determined by f_heuristics function 
        
        if not self.successors is None:
            print 'REAL'
            return self.successors, self.costs 
        
        successors = []
        costs = []
        
        # each domain to each node except its own 
        for d in xrange(len(self.domains)): 
            for node in xrange(len(self.nodeload)): 
                nodes = list(self.nodeload)
                domains = list(self.domains)
                
                if domains[d] == node:
                    continue
                
                # remove from source node
                currnode = domains[d]
                nodes[currnode] -= self.domainload[d]
                # add to target node
                nodes[node] += self.domainload[d]
                # Change node of domain
                domains[d] = node
                
                # Check overload constraint
                if nodes[node] > 100:
                    continue 
                
                cost = 1
                # cost += 0.5 * (nodes[node] / 100.0) # increases expansions 
                if target.domains[d] == self.domains[d]: # decreases expansions
                    cost += 3
                elif target.domains[d] == domains[d]:
                    cost -= 1
                elif nodes[node] == 0:
                    cost -= 1
                elif nodes[node] > 80:
                    cost += 1
                    
                new = ANode(nodes, domains, self.domainload)
                
                # Check constraints
                                
                # check if node is in mesh already
                test = mesh.find(new)
                if test:
                    new = test
                else:
                    new.predecessor = self
                    mesh.put(new)
                    
                successors.append(new)
                costs.append(cost)
        
        self.successors = successors
        self.costs = costs
        return (successors, costs)
       
    def __eq__(self, another):
        if another == None:
            return False
        
        return self.domains == another.domains
    
    def __hash__(self):
        if self.hash:
            return self.hash
        
        h = 0
        for i, v in enumerate(self.domains):
            h += (i + 1) * v
            
        self.hash = h 
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
        expansions = 0
        try:
            while True:
                # sys.stdout.write('.') 
                value = self.openlist.top_one()
                if value is None:
                    print 'nothing found again'
                    print 'expansions %i' % expansions
                    return
                
                if value == end:
                    print 'END FOUND.... run backtracking now'
                    print 'expansions %i' % expansions
                    return end
                
                if (expansions % 50) == 0:
                    print 'expansions %i' % expansions
                
                expansions += 1
                self.expand(value)
                self.closelist.add(value)  
                
        except KeyError:
            pass
                    
        print 'nothing found'
        
    
    def expand(self, current):
        successors, costs = current.get_successors(self.mesh, self.end)
        for i in xrange(len(successors)):
            successor = successors[i] 
            if successor in self.closelist:
                continue
            
            # Relaxion on costs
            new_g = current.g + costs[i]
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
                self.openlist.put(successor, f, False)
        
        self.openlist.heap() 

def main():
    # Create initial state
#    nodes = 50
#    domainc = 50
#    
#    domains = []
#    domainl = []
#    nodel = [0 for _ in xrange(nodes)]
#    
#    for i in xrange(domainc):
#        while True: 
#            import random
#            node = random.randint(0, nodes-1)
#            load = abs(random.randint(0, 50-1))
#            if (nodel[node] + load) > 100:
#                continue
#            domains.append(node)
#            domainl.append(load)
#            nodel[node] += load
#            break
#        
#    nodel.append(0)
    
    nodes = 6
    domains = [1,2,2,3,4,5]
    target = [2,1,2,3,5,4]
    
    domainl = [90,20,00,0,90,20]
    
    nodel = [0 for _ in xrange(nodes)]
    for i in xrange(len(domains)):
        nodel[domains[i]] += domainl[i]
    
    print domains
    print domainl
    print nodel
    print 'A*'
        
    # Create target state
#    target = list(domains)
#    target[3] = 1
    
    
    # Validate overload
    targetl = [0 for _ in xrange(nodes)]
    for i, v in enumerate(target):
        targetl[v] += domainl[i]
        
    for i in targetl:
        if i > 100:
            print 'INVALID TARGET STATE' 
            return
    
        
    # Create target and end node
    print list(nodel)
    start = ANode(nodel, domains, domainl)
    target = ANode(nodel, target, domainl)
    
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


def plan(node_count, start, target, domain_load):
    print start
    print target
    
    # Calulate the nodes load for the start allocation
    nodes_load = [0 for _ in xrange(node_count)]
    for i in xrange(len(start)):
        nodes_load[start[i]] += domain_load[i]
    
    # Create A* nodes for the search
    start = ANode(nodes_load, start, domain_load)
    target = ANode(nodes_load, target, domain_load)
    
    # Create a new mesh with start and target nodes
    mesh = Mesh()
    mesh.put(start)
    mesh.put(target)
    
    # Run A*
    s = AStar()
    end = s.search(mesh, start, target)
    
    # Extract migrations from A*
    migrations = []
    while True:
        predecessor = end.predecessor
        if end.predecessor == None:
            break
        
        for domain, server in enumerate(end.domains):
            if predecessor.domains[domain] != server:
                migration = (domain, predecessor.domains[domain], server)
                migrations.append(migration)
                break
        
        end = predecessor
        
    print migrations
    return reversed(migrations)

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
    domainload = [0 for _ in xrange(10)]
    
    domains = [0, 1, 2, 1, 2, 1]
    domainl = [10, 20, 30, 10, 40, 20]
    
    for i, domain in enumerate(domains):
        nodes[domain] += domainl[i]
        
    print nodes
    
    # Calc initial node load
    
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
    # testNode()
    for i in xrange(1):
        main()
    
        
        
    
