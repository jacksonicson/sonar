from control.logic import scoreboard
import configuration_advanced

class MigrationScheduler():
    
    def __init__(self, controller):
        self.controller = controller
        self.migration_queue = []

    def add_migration(self, domain, source, target, migration_type, depends=None):
        migration = self.Migration()
        migration.domain = domain
        migration.source = source
        migration.target = target
        migration.migration_type = migration_type
        migration.triggered = False
        migration.depends = depends
        
        # check if there is already a migration in the queue that wants to migrate the same domain
        for mig in self.migration_queue:
            if mig.domain == migration.domain:
                return
        self.migration_queue.append(migration)
        self.migration_scheduler()
        
        return migration
        
    def finish_migration(self, success, domain, source, target):
        for mig in self.migration_queue:
            if domain == mig.domain and source == mig.source and target == mig.target:
                if success == True:
                    scoreboard.Scoreboard().add_migration_type(mig.migration_type)
                self.migration_queue.remove(mig)
                self.migration_scheduler()   
        
    def migration_scheduler(self):
        print 'START SCHEDULER; %s MIGRATIONS TO DO' % (len(self.migration_queue))
        for migration in self.migration_queue:
            print 'domain: %s; source: %s; target: %s; migration_type: %s; triggered: %s' % (migration.domain.name, migration.source.name, migration.target.name, migration.migration_type, migration.triggered)
        
        for migration in self.migration_queue:    
            
            if migration.triggered:
                # migration already triggered, but not finished yet
                continue
                   
            skip = False           
            for another_migration in self.migration_queue:
                test = True
                test &= (another_migration != migration)
                test &= (another_migration.triggered == True)
                test &= ((another_migration.target == migration.target) or (another_migration.source == migration.source))
                test |= (another_migration == migration.depends)
                if test:
                    skip = True

            if skip == True:
                continue
            
            print '%s migration: %s from %s to %s' % (migration.migration_type, migration.domain.name, migration.source.name, migration.target.name)
            migration.triggered = True
            self.controller.migrate(migration.domain, migration.source, migration.target, configuration_advanced.K_VALUE) 
            
    class Migration(object):
        pass