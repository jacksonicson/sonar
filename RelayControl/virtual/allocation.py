from libvirt import VIR_MIGRATE_LIVE, VIR_MIGRATE_UNDEFINE_SOURCE, \
    VIR_MIGRATE_PERSIST_DEST
import libvirt
import nodes
import sys
import time
import traceback
import control.domains as domains
from threading import Thread

# Global connections variable
connections = None

# Error handler for libvirt
def handler(ctxt, err):
    print 'Libvirt error'
    print err
    print ctxt
    
# Register error handler in libvirt
libvirt.registerErrorHandler(handler, 'context') 


def __find_domain(connections, domain_name):
    last = None, None
    for connection in connections.values():
        try:
            domain = connection.lookupByName(domain_name)
            last = domain, connection
            
            state = domain.state(0)[0]
            if state == 1:
                return domain, connection
        except:
            pass
        
    return last


class MigrationThread(Thread):
    def __init__(self, domain, node_from, node_to, migration_callback, info):
        super(MigrationThread, self).__init__()
        self.domain = domain
        self.node_from = node_from
        self.node_to = node_to
        self.migration_callback = migration_callback
        self.info = info
        self.exited = False
    
    def run(self):
        self.start = time.time()
        
        # Create connections
        from virtual import util
        connection_from = util.connect(self.node_from)
        connection_to = util.connect(self.node_to)
        
        # Domain to migrate
        domain = connection_from.lookupByName(self.domain)
        
        success = True
        error = None
        try:
            self.tomigrate = domain
            domain = domain.migrate(connection_to, VIR_MIGRATE_LIVE | VIR_MIGRATE_UNDEFINE_SOURCE | VIR_MIGRATE_PERSIST_DEST, self.domain, None, 0)
            self.end = time.time()
        except Exception as e:
            self.end = time.time()
            success = False
            error = e
        finally:
            print 'Calling back...'
            self.migration_callback(self.domain, self.node_from, self.node_to, self.start, self.end, self.info, success, error)
            
            util.close(connection_from)
            util.close(connection_to)
            
            self.exited = True
                

def migrateDomain(domain, node_from, node_to, migration_callback, info=None, maxDowntime=60000):
    # Start a new migration thread
    thread = MigrationThread(domain, node_from, node_to, migration_callback, info)
    thread.start()
    
    # Set the max downtime after migration has started
    while thread.exited == False:
        time.sleep(1)
        
        try:
            thread.tomigrate.migrateSetMaxDowntime(maxDowntime, 0)
            print 'Max migration time set to %i' % maxDowntime
            break
        except:
            pass
    

'''
Gets a list of migrations. Each list element is a tupel of the structure: 
(domain name, target host index from the nodes model)
'''
def migrateAllocation(migrations):
    try:
        # Connect with all servers
        from virtual import util
        connections = util.connect_all()
        
        # trigger migrations
        for migration in migrations:
            domain_name = migration[0]
            target_node = nodes.get_node_name(migration[1])
            
            # Search the node which currently holds the domain
            domain, _ = __find_domain(connections, domain_name)
            if domain == None:
                print 'WARN: skipping - domain not found: %s' % (domain_name)
                continue
            
            # If not running start on source (necessary for migrations?)
            state = domain.state(0)[0]
            if state != 1:
                # Destroy 
                print 'Resetting the domain %s' % (domain_name)
                try:
                    domain.destroy()
                except: pass
                
                # Start
                try:
                    domain.create()
                    time.sleep(10)
                except: pass
            
            # Undefine target domain if it already exists
            try:
                dom_target = connections[target_node].lookupByName(domain_name)
                if dom_target != None:
                    dom_target.undefine()
                    print 'Undefined already exiting target domain'
            except:
                pass
            
            # Migrate to target
            try:
                print 'Migrating domain: %s to node: %s ...' % (domain_name, connections[target_node].getHostname())
                domain = domain.migrate(connections[target_node],
                                        VIR_MIGRATE_LIVE | VIR_MIGRATE_UNDEFINE_SOURCE | VIR_MIGRATE_PERSIST_DEST,
                                        domain_name, None, 0)
                print 'Migration successful'
            except:
                traceback.print_exc(file=sys.stdout)
                print 'Skipping - migration failed'
            
    except:
        traceback.print_exc(file=sys.stdout)
    finally:
        # Close connections
        util.close_all(connections)


def determine_current_allocation():
    try:
        # Connect with all servers
        from virtual import util
        connections = util.connect_all()
        
        allocation = { host : [] for host in nodes.HOSTS }
            
        for host in nodes.HOSTS:
            connection = connections[host]
            
            vir_domains = connection.listDomainsID()
            for vir_id in vir_domains:
                vir_domain = connection.lookupByID(vir_id)
                name = vir_domain.name()
                if domains.has_domain(name):
                    # print 'adding mapping with %s' % name
                    allocation[host].append(name)
                else:
                    print 'ERROR: Domain %s is not in the domain list!' % name
    finally:
        print 'Closing connections...'
        util.close_all(connections)
    
    return allocation
    
    
if __name__ == '__main__':
    determine_current_allocation()
    pass
