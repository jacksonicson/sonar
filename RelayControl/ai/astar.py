import heapq
import itertools
from sets import Set

class PriorityQueue(object):
    def __init__(self):
        self.pq = []                         # list of entries arranged in a heap
        self.entry_finder = {}               # mapping of tasks to entries
        self.REMOVED = '<removed-task>'      # placeholder for a removed task
        self.counter = itertools.count()     # unique sequence count
    
    def has(self, task):
        return task in self.entry_finder
    
    def add_task(self, task, priority=0):
        'Add a new task or update the priority of an existing task'
        if task in self.entry_finder:
            self.remove_task(task)
        count = next(self.counter)
        entry = [priority, count, task]
        self.entry_finder[task] = entry
        heapq.heappush(self.pq, entry)
    
    def remove_task(self,task):
        'Mark an existing task as REMOVED.  Raise KeyError if not found.'
        entry = self.entry_finder.pop(task)
        entry[-1] = self.REMOVED
    
    def pop_task(self):
        'Remove and return the lowest priority task. Raise KeyError if empty.'
        while self.pq:
            priority, count, task = heapq.heappop(self.pq)
            if task is not self.REMOVED:
                del self.entry_finder[task]
                return task
        raise KeyError('pop from an empty priority queue')

class ANode(object):
    def __init__(self, value):
        self.successors = []
        self.predecessor = None
        self.costs = []
        self.value = value
        self.g = 9999
        
    def dump(self):
        print self.value
        
    def add(self, successor, cost=1):
        self.successors.append(successor)
        self.costs.append(cost)
        successor.attachTo(self)
        
    def attachTo(self, predecessor):
        self.predecessor = predecessor


class AStar(object):
    def __init__(self):
        self.openlist = PriorityQueue()
        self.closelist = Set()
    
    def search(self, graph, start, end):
        self.openlist.add_task(start, 0)
        
        while True: 
            value = self.openlist.pop_task()
            value.dump
            
            if value == end:
                return end
            
            self.expand(value)
            self.closelist.add(value)  
            
            if not self.openlist:
                break
    
    def h(self, successor):
        return 1
    
    def expand(self, current):
        for i in xrange(len(current.successors)):
            successor = current.successors[i] 
            if successor in self.closelist:
                print 'Continouing closed list value'
                continue
            
            new_g = current.g + current.costs[i]
            
            # New costs are more expensive - skip
            if self.openlist.has(successor) and new_g >= successor.g:
                continue
            
            # Update predecessor for backtracking
            successor.predecessor = current
            successor.g = new_g
            
            # Update open list
            f = new_g + self.h(successor)
            if self.openlist.has(successor):
                self.openlist.add_task(successor, f) 
            else:
                self.openlist.add_task(successor, f)
             
    

if __name__ == '__main__':
    a = ANode('a')
    c = ANode('c')
    d = ANode('d')
    b = ANode('b')
    
    a.add(c, 4)
    a.add(d, 20)
    
    c.add(b, 100000)
    d.add(b, 300)
    
    # Der suchbaum muss komplett aufgespannt werden (FEAR code kucken ob das so ist)
    # Migrationskosten = Gewichte
    # Heursitik = Delta - bevorzugen von aktionen mit direktem einfluss auf den end state
    
    s = AStar()
    end = s.search(None, a, b)
    while True: 
        print end.value
        if not end.predecessor:
            break
        end = end.predecessor
    
