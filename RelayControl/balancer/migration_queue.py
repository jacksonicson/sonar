import scoreboard

class Entry(object):
    def __init__(self, domain, source_node, target_node, description=None):
        self.domain = domain
        self.source = source_node
        self.target = target_node
        self.description = description
        
    def __eq__(self, other):
        test = True
        test &= self.domain == other.domain
        test &= self.source == other.source
        test &= self.target == other.target
        return test
        

class MigrationQueue():
    
    def __init__(self, controller):
        # Reference to the controller
        self.controller = controller
        
        # Migration queue
        self.waiting = []
        self.running = []

    def add(self, domain, source_node, target_node, description=None):
        entry = Entry(domain, source_node, target_node, description)

        # Schedule
        self.waiting.append(entry)
        self._schedule()
        
    def finished(self, success, domain, source_node, target_node):
        entry = Entry(domain, source_node, target_node)
        for migration in self.running:
            if migration == entry: 
                self.running.remove(migration)
                break
        
        self._schedule()
        
    def _schedule(self):
        print 'Scheduling migrations...'
        
        to_trigger = []
        for i, migration in enumerate(self.waiting):
            
            # Check if complies with running migrations
            skip = False
            for test in self.running:
                skip |= test.source == migration.source
                
            if skip:
                continue 
            
            del self.waiting[i]
            self.running.append(migration)
            to_trigger.append(migration)
                
        # Trigger migrations
        for migration in to_trigger:
            self.controller.migrate(migration.domain, migration.source,
                                    migration.target, 20)
            
  
if __name__ == '__main__':
    class MockController(object):
        
        def __init__(self):
            self.q = MigrationQueue(self)
            
        def test(self):
            self.q.add('test0', 'node0', 'node1')
            self.q.add('test2', 'node0', 'node1')
            self.q.add('test1', 'node1', 'node2')
            
        def migration_finished(self, domain, source, target, kvalue):
            self.q.finished(True, domain, source, target)
        
        def migrate(self, domain, source, target, kvalue):
            print 'migrate: %s' % domain
            self.migration_finished(domain, source,target,kvalue)
        
    c = MockController()
    c.test()
    
              
