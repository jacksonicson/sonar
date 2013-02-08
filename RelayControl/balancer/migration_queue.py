class Entry(object):
    def __init__(self, domain, source_node, target_node, depends=None, description=None):
        self.domain = domain
        self.source = source_node
        self.target = target_node
        self.description = description
        self.depends = depends
        self.retries = 0 
        
    def __eq__(self, other):
        if other == None:
            return False
        
        test = True
        test &= self.domain == other.domain
        test &= self.source == other.source
        test &= self.target == other.target
        return test
        

class MigrationQueue(object):
    
    def __init__(self, controller, double=False, restrict=False):
        # Reference to the controller
        self.controller = controller
        
        # Restirct double migrations
        self.double = double
        
        # Restirct parallelity
        self.restrict = restrict
        
        # Migration queue
        self.waiting = []
        self.running = []

    def empty(self):
        return len(self.waiting) == 0 and len(self.running) == 0


    def flush(self):
        del self.waiting[:]


    def add(self, domain, source_node, target_node, depends=None, description=None):
        entry = Entry(domain, source_node, target_node, depends, description)

        # Filter unnecessary migrations
        append = (source_node != target_node)

        # Schedule if valid entry
        if append:
            self.waiting.append(entry)
            self._schedule()
        
        # Return entry for dependencies
        return entry
        
    def finished(self, success, domain, source_node, target_node):
        entry = Entry(domain, source_node, target_node)
        for migration in self.running:
            if migration == entry: 
                self.running.remove(migration)
                if not success:
                    migration.retries += 1
                    if migration.retries < 3:
                        print 'WARN: Migration failed, retrying...'
                        self.waiting.append(migration)
                    else:
                        print 'WARN: Migration failed too often - CANCEL MIGRATION'
                    
                self._schedule()
        print 'ERROR'
        
        
    def _schedule(self):
        print 'Scheduling migrations...'
        print 'Waiting migrations: %i' % (len(self.waiting) + len(self.running))
        
        to_trigger = []
        for i, migration in enumerate(self.waiting):
            
            # Check if complies with running migrations
            skip = False
            
            if self.double:
                for test in self.running:
                    # One outgoing migration per server
                    skip |= test.source == migration.source
                    skip |= test.target == migration.target
                    skip |= test.domain == migration.domain

            # Check if migration intersects with previous migrations
            if self.restrict:
                to_check = []
                to_check.extend(self.running)
                to_check.extend(self.waiting[:i])
                
                for previous in to_check:
                    test = False
                    test |= previous.domain == migration.domain
                    test |= previous.source == migration.source
                    test |= previous.target == migration.target
                    
                    # Update skip 
                    skip |= test
                    
            if not skip:
                print 'Test is false: %s: %s - %s' % (migration.domain.name, migration.source.name, migration.target.name)

            # Check dependencies
            if migration.depends != None: 
                skip |= migration.depends in self.waiting
                skip |= migration.depends in self.running
                
            if not skip:
                self.running.append(migration)
                to_trigger.append(migration)
            else:
                pass
            
        # Trigger migrations
        for migration in to_trigger:
            self.waiting.remove(migration)
            self.controller.migrate(migration.domain, migration.source,
                                    migration.target)
            
  
if __name__ == '__main__':
    class MockController(object):
        def __init__(self):
            self.q = MigrationQueue(self)
            
        def test(self):
            a = self.q.add('test0', 'node0', 'node1')
            self.q.add('test2', 'node0', 'node1', a)
            self.q.add('test1', 'node1', 'node2')
            
        def migration_finished(self, domain, source, target):
            self.q.finished(True, domain, source, target)
        
        def migrate(self, domain, source, target):
            print 'migrate: %s' % domain
            self.migration_finished(domain, source, target)
        
    c = MockController()
    c.test()
    
              
