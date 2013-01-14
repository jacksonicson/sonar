from control.logic import scoreboard
import configuration_advanced

class MigrationScheduler():
    
    def __init__(self, controller):
        self.controller = controller
        self.migration_queue = []

    def add_migration(self, domain, source, target, migration_type, depends=None):
        # check if there is already a migration in the queue that wants to migrate the same domain
        for mig in self.migration_queue:
            if mig.domain == domain:
                return
        
        # create migration object
        migration = self.Migration()
        migration.domain = domain
        migration.source = source
        migration.target = target
        migration.migration_type = migration_type
        migration.triggered = False
        migration.depends = depends
        
        # add migration to queue and run scheduler
        self.migration_queue.append(migration)
        self.migration_scheduler()
        
        return migration
        
    def finish_migration(self, success, domain, source, target):
        # find finished migration in queue
        for mig in self.migration_queue:
            if domain == mig.domain and source == mig.source and target == mig.target:
                
                if success == True:
                    # if migration successful, add migration_type to scoreboard
                    migration_type = str(mig.migration_type)
                    scoreboard.Scoreboard().add_migration_type(migration_type)
                    
                # remove migration from queue and run scheduler
                self.migration_queue.remove(mig)
                self.migration_scheduler()   
        
    def migration_scheduler(self):
        for migration in self.migration_queue:    
            if migration.triggered:
                # migration already triggered
                continue
                   
            skip = False           
            for another_migration in self.migration_queue:
                # migration cannot be triggered if source or target node are part of an ongoing migration
                test = True
                test &= (another_migration != migration)
                test &= (another_migration.triggered == True)
                test &= ((another_migration.target == migration.target) or (another_migration.source == migration.source))
               
                # migration cannot be triggered if it depends on a migration
                test |= (another_migration == migration.depends)
                
                if test:
                    skip = True
                    break
            if skip == True:
                continue
            
            # migrate and set triggered true
            self.controller.migrate(migration.domain, migration.source, migration.target, configuration_advanced.K_VALUE) 
            migration.triggered = True
            
    class Migration(object):
        pass