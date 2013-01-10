import scoreboard

class migration():
    
    def __init__(self, controller, k_value):
        self.controller = controller
        self.K_VALUE = k_value
        self.migration_queue = []

    def add_migration(self, domain, source, target, migration_type):
        migration = {
                'domain' : domain,
                'source' : source,
                'target' : target,
                'migration_type' : migration_type,
                'triggered' : False,
                'finished' : False
                }
        
        # check if there is already a migration in the queue that wants to migrate the same domain
        for mig in self.migration_queue:
            if mig['domain'].name == migration['domain'].name:
                return
        self.migration_queue.append(migration)
        self.migration_scheduler()
        
    def finish_migration(self, success, domain, source, target):
        for mig in self.migration_queue:
            if domain == mig['domain'] and source == mig['source'] and target == mig['target']:
                if success == True:
                    scoreboard.Scoreboard().add_migration_type(mig['migration_type'])
                self.migration_queue.remove(mig)
                self.migration_scheduler()   
        
    def migration_scheduler(self):
        print 'START SCHEDULER; %s MIGRATIONS TO DO' % (len(self.migration_queue))
        for migration in self.migration_queue:
            print migration
            print 'domain: %s; source: %s; target: %s; migration_type: %s; triggered: %s; finished: %s' % (migration['domain'].name, migration['source'].name, migration['target'].name, migration['migration_type'], migration['triggered'], migration['finished'])
        
        for migration in self.migration_queue:    
            domain = migration['domain']
            source = migration['source']
            target = migration['target']
            migration_type = migration['migration_type']
            triggered = migration['triggered']
            finished = migration['finished']
            
            skip = False           
            for another_migration in self.migration_queue:
                target2 = another_migration['target']
                triggered2 = another_migration['triggered']
                finished2 = another_migration['finished']
                
                if migration != another_migration and target.name == target2.name and finished2 == False and triggered2 == True:
                    # There is another migration with same target node that is already triggered but not finished yet 
                    skip = True
     
            if skip == True or triggered == True:
                continue
            
            print '%s migration: %s from %s to %s' % (migration_type, domain.name, source.name, target.name)
            migration['triggered'] = True
            self.controller.migrate(domain, source, target, self.K_VALUE) 