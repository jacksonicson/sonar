from analytics import forecasting as smoother
from logs import sonarlog
from model import types
import configuration
import controller
import json
import numpy as np

######################
## CONFIGURATION    ##
######################
if configuration.PRODUCTION:
    START_WAIT = 120
    INTERVAL = 30
    
    THRESHOLD_OVERLOAD = 90
    THRESHOLD_UNDERLOAD = 30
    
    PERCENTILE = 80.0
    THR_PERCENTILE = 0.2

else:
    
    START_WAIT = 10 * 60
    INTERVAL = 5 * 60
    THRESHOLD_OVERLOAD = 90
    THRESHOLD_UNDERLOAD = 40
    PERCENTILE = 80.0
    THR_PERCENTILE = 0.2
######################

# Setup logging
logger = sonarlog.getLogger('controller')

class Sandpiper(controller.LoadBalancer):
    
    def __init__(self, pump, model):
        super(Sandpiper, self).__init__(pump, model, INTERVAL, START_WAIT)
        self.var = []
        
    def dump(self):
        print 'Dump Sandpiper controller configuration...'
        logger.info('Controller Configuration: %s' % json.dumps({'name' : 'Sandpiper',
                                                                 'start_wait' : START_WAIT,
                                                                 'interval' : INTERVAL,
                                                                 'threshold_overload' : THRESHOLD_OVERLOAD,
                                                                 'threshold_underload' : THRESHOLD_UNDERLOAD,
                                                                 'percentile' : PERCENTILE,
                                                                 'thr_percentile' : THR_PERCENTILE,
                                                                 }))
    
    def initial_placement_sim(self):
        import placement
        from virtual import nodes
        from control import domains 
        
        nodecount = len(nodes.HOSTS)
        splace = placement.FirstFitPlacement(nodecount, nodes.NODE_CPU, nodes.NODE_MEM, nodes.DOMAIN_MEM)
        migrations, _ = splace.execute()
        
        _nodes = []
        for node in nodes.NODES: 
            mnode = self.model.Node(node, nodes.NODE_CPU_CORES)
            _nodes.append(mnode)
            
        _domains = {}
        for domain in domains.domain_profile_mapping:
            dom = self.model.Domain(domain.domain, nodes.DOMAIN_CPU_CORES)
            _domains[domain.domain] = dom
            
        for migration in migrations:
            print migration 
            _nodes[migration[1]].add_domain(_domains[migration[0]])
            
        return migrations 
    
    
    def post_migrate_hook(self, success, domain, node_from, node_to, end_time):
        if success:
            # Release block
            node_from.blocked = end_time
            node_to.blocked = end_time
            
            # Reset CPU consumption: Necessary because the old CPU readings
            # may trigger another migrations as they do not represent the load
            # without the VM
            node_from.flush(50)
            node_to.flush(50)
            print self.var
        else:
            node_from.blocked = end_time
            node_to.blocked = end_time
        
    
    def check_imbalance(self, time_now, sleep_time, k):    
        nodes = self.model.get_hosts(self.model.types.NODE)
        readings = []
        for node in nodes:
            readings.append(node.forecast())
            
        sd = np.std(readings)
        if sd > 40:
            best_fnode = None
            best_tnode = None
            best_domain = None
            best = 200
            for fnode in nodes:
                for domain in fnode.domains.values():
                    for tnode in nodes:
                        if fnode == tnode:
                            continue
                        
                        if not tnode.domains:
                            continue
                        
                        domain_cpu_factor = tnode.cpu_cores / domain.cpu_cores
                        test = True
                        test &= (tnode.forecast() + domain.forecast() / domain_cpu_factor) < THRESHOLD_OVERLOAD # Overload threshold
                        test &= len(tnode.domains) < 6
                        test &= (time_now - tnode.blocked) > sleep_time
                        test &= (time_now - tnode.blocked) > sleep_time
                        test &= (time_now - fnode.blocked) > sleep_time
                        test &= (time_now - fnode.blocked) > sleep_time
                        
                        if test == False: 
                            continue
                        
                        readings = []
                        readings.append(fnode.forecast() - domain.forecast() / 2.0)
                        readings.append(tnode.forecast() + domain.forecast() / 2.0)
                        
                        for cnode in nodes:
                            if cnode == fnode: continue
                            if cnode == tnode: continue
                            readings.append(node.percentile_load(PERCENTILE, k))
                        
                        sd = np.std(readings)
                        if sd < best:
                            best_fnode = fnode
                            best_tnode = tnode
                            best_domain = domain
                            best = sd
                            
            if best < 200: 
                self.migrate(best_domain, best_fnode, best_tnode, k)
                return True
            
        return False
                        
                    
    
    def check_hostpost(self, k):
        for node in self.model.get_hosts(types.NODE):
            # Check past readings
            readings = node.get_readings()
            
            # Calculate percentile on the data
            slc = readings[-k:]
            
            forecast = smoother.single_exponential_smoother(slc)[0]
            forecast = smoother.double_exponential_smoother(slc)[0]
            forecast = node.forecast()
            forecast = np.mean(slc)
            forecast = smoother.ar_forecast(slc)
            
            percentile = node.forecast()# np.percentile(slc, THR_PERCENTILE)
            percentile_ = node.forecast() # np.percentile(slc, 1 - THR_PERCENTILE)
            
            overload = (percentile > THRESHOLD_OVERLOAD)
            underload = (percentile_ < THRESHOLD_UNDERLOAD)
            overload = (overload and forecast > THRESHOLD_OVERLOAD)
            underload = (underload and forecast < THRESHOLD_UNDERLOAD)
             
            if overload:
                print 'Overload in %s - %s' % (node.name, slc)  
             
            # Update overload                                
            node.overloaded = overload
            node.underloaded = underload
    
    def migration_trigger(self, overload, nodes, node, k, sleep_time, time_now):
        # Source node to migrate from 
        source = node
        
        # Sort domains by their VSR value in decreasing order 
        node_domains = []
        node_domains.extend(node.domains.values())
        node_domains.sort(lambda a, b: int(b.volume_size - a.volume_size))
        
        # Try to migrate all domains by decreasing VSR value
        for domain in node_domains:
            if overload: 
                targets = reversed(range(nodes.index(node) + 1, len(nodes)))
            else:
                targets = range(nodes.index(node) - 1)
            
            # Try all targets for the migration (reversed - starting at the BOTTOM)
            for target in targets:
                target = nodes[target]
                
                if len(target.domains) == 0:
                    continue
                 
                domain_cpu_factor = target.cpu_cores / domain.cpu_cores
                 
                test = True
                test &= (target.percentile_load(PERCENTILE, k) + domain.percentile_load(PERCENTILE, k) / domain_cpu_factor) < THRESHOLD_OVERLOAD # Overload threshold
                test &= len(target.domains) < 6
                blocked = True
                blocked &= (time_now - target.blocked) > sleep_time
                blocked &= (time_now - source.blocked) > sleep_time
                test &= blocked
                
                if test: 
                    print 'Overload migration: %s from %s to %s' % (domain.name, source.name, target.name)
                    self.migrate(domain, source, target, k)
                    raise StopIteration()
                else:
                    print 'No overload migration: %s - %i' % (target.name, blocked)
                
            for target in targets:
                target = nodes[target]
                 
                domain_cpu_factor = target.cpu_cores / domain.cpu_cores
                 
                test = True
                test &= (target.percentile_load(PERCENTILE, k) + domain.percentile_load(PERCENTILE, k) / domain_cpu_factor) < THRESHOLD_OVERLOAD # Overload threshold
                test &= len(target.domains) < 6
                blocked = True
                blocked &= (time_now - target.blocked) > sleep_time
                blocked &= (time_now - source.blocked) > sleep_time
                test &= blocked
                
                if test: 
                    print 'Overload migration (Empty): %s from %s to %s' % (domain.name, source.name, target.name)
                    self.migrate(domain, source, target, k)
                    raise StopIteration()
                else:
                    print 'No overload migration: %s - %i' % (target.name, blocked)
    
    def balance(self):
        ############################################
        ## HOTSPOT DETECTOR ########################
        ############################################
        k = 40
        self.check_hostpost(k)
        
        ############################################
        ## MIGRATION MANAGER #######################
        ############################################
        # Calculate volumes of each node
        nodes = []
        domains = []
        for node in self.model.get_hosts():
            volume = 1.0 / max(0.001, float(100.0 - node.percentile_load(PERCENTILE, k)) / 100.0)
            node.volume = volume
            node.volume_size = volume / 8.0 # 8 GByte
            
            if node.type == types.NODE:
                nodes.append(node)
            elif node.type == types.DOMAIN: 
                domains.append(node)
       
        # Sort nodes to their volume in DECREASING order
        # Multiplication with a big value to shift post comma digits to the front (integer)
        nodes.sort(lambda a, b: int((b.volume - a.volume) * 100000))
        
        ############################################
        ## MIGRATION TRIGGER #######################
        ############################################
        time_now = self.pump.sim_time()
        sleep_time = 30
        for node in nodes:
            node.dump()
            
            try:
                # Overload situation
                if node.overloaded:
                    self.migration_trigger(True, nodes, node, k, sleep_time, time_now)
            except StopIteration: pass 
            
            # Balance system
            self.check_imbalance(time_now, sleep_time, k)
            
            try:
                # Underload situation
                if node.underloaded:
                    self.migration_trigger(False, nodes, node, k, sleep_time, time_now)
            except StopIteration: pass
            
