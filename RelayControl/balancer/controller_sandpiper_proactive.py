from analytics import forecasting as smoother
from logs import sonarlog
from model import types
from virtual import placement, nodes
import controller
import json
import numpy as np

######################
# # CONFIGURATION    ##
######################
START_WAIT = 120 
INTERVAL = 300

THRESHOLD_OVERLOAD = 90
THRESHOLD_UNDERLOAD = 40

PERCENTILE = 80.0

THR_PERCENTILE = 0.10
K_VALUE = 20  # sliding windows size
M_VALUE = 17  # m values out of the window k must be above or below the threshold
######################

# Setup logging
logger = sonarlog.getLogger('controller')

class Controller(controller.LoadBalancer):
    
    def __init__(self, scoreboard, pump, model):
        super(Controller, self).__init__(scoreboard, pump, model, INTERVAL, START_WAIT)
        self.var = []
        
    def dump(self):
        print 'Dump Sandpiper controller configuration...'
        logger.info('Controller Configuration: %s' % json.dumps({'name' : 'Sandpiper Proactive',
                                                                 'start_wait' : START_WAIT,
                                                                 'interval' : INTERVAL,
                                                                 'threshold_overload' : THRESHOLD_OVERLOAD,
                                                                 'threshold_underload' : THRESHOLD_UNDERLOAD,
                                                                 'percentile' : PERCENTILE,
                                                                 'thr_percentile' : THR_PERCENTILE,
                                                                 }))
    
    def initial_placement(self):
        nodecount = len(nodes.NODES)
        splace = placement.FirstFitPlacement(nodecount, nodes.NODE_CPU, nodes.NODE_MEM, nodes.DOMAIN_MEM)
        return splace.execute()
    
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
                        test &= (tnode.forecast() + domain.forecast() / domain_cpu_factor) < THRESHOLD_OVERLOAD  # Overload threshold
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
                self.migrate(best_domain, best_fnode, best_tnode)
                return True
            
        return False
                        
                    
    
    def check_hostpost(self, k):
        for node in self.model.get_hosts(types.NODE):
            # Check past readings
            readings = node.get_readings()
            
            # Calculate percentile on the data
            slc = readings[-k:]
            
            forecast = smoother.single_exponential_smoother(slc)[0]
            forecast = node.forecast()
            forecast = smoother.ar_forecast(slc)
            forecast = np.mean(slc)
            forecast = smoother.double_exponential_smoother(slc)[0]
            
#            percentile = np.percentile(slc, THR_PERCENTILE)
#            percentile_ = np.percentile(slc, 1 - THR_PERCENTILE)
#            overload = (percentile > THRESHOLD_OVERLOAD)
#            underload = (percentile_ < THRESHOLD_UNDERLOAD)

            k = K_VALUE
            overload = 0
            underload = 0
            for reading in readings[-k:]:
                if reading > THRESHOLD_OVERLOAD: overload += 1
                if reading < THRESHOLD_UNDERLOAD: underload += 1
            
            m = M_VALUE
            overload = (overload >= m)
            underload = (underload >= m)
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
                # walk reversed [::-1] from bottom to the top (low load to high load)
                targets = range(nodes.index(node) + 1, len(nodes))[::-1]
            else:
                # walk reversed [::-1] from bottom to the top (low load to high load) 
                targets = range(nodes.index(node))[::-1]
            
            print 'Potential target nodes for domain %s: ' % domain.name
            for target in targets:
                target = nodes[target]
                print target.name
            
            # Try all targets for the migration
            for target in targets:
                target = nodes[target]
                if len(target.domains) == 0:
                    continue
                
                domain_cpu_factor = target.cpu_cores / domain.cpu_cores
                 
                test = True
                test &= (target.percentile_load(PERCENTILE, k) + domain.percentile_load(PERCENTILE, k) / domain_cpu_factor) < THRESHOLD_OVERLOAD  # Overload threshold
                test &= len(target.domains) < 6
                test &= (time_now - target.blocked) > sleep_time
                test &= (time_now - source.blocked) > sleep_time
                
                if test: 
                    print 'Overload migration: %s from %s to %s' % (domain.name, source.name, target.name)
                    self.migrate(domain, source, target)
                    raise StopIteration()
                
            for target in targets:
                target = nodes[target]
                 
                domain_cpu_factor = target.cpu_cores / domain.cpu_cores
                 
                test = True
                test &= (target.percentile_load(PERCENTILE, k) + domain.percentile_load(PERCENTILE, k) / domain_cpu_factor) < THRESHOLD_OVERLOAD  # Overload threshold
                test &= len(target.domains) < 6
                test &= (time_now - target.blocked) > sleep_time
                test &= (time_now - source.blocked) > sleep_time
                
                if test: 
                    print 'Overload migration (Empty): %s from %s to %s' % (domain.name, source.name, target.name)
                    self.migrate(domain, source, target)
                    raise StopIteration()
    
    
    def balance(self):
        ############################################
        ## HOTSPOT DETECTOR ########################
        ############################################
        k = 20
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
            node.volume_size = volume / 8.0  # 8 GByte
            
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
        sleep_time = 60
        for node in nodes:
            node.dump()
            
            try:
                # Overload situation
                if node.overloaded:
                    print 'Overload...'
                    self.migration_trigger(True, nodes, node, k, sleep_time, time_now)
            except StopIteration: pass 
            
            # Balance system
            print 'Imbalance...'
            # self.check_imbalance(time_now, sleep_time, k)
            
            try:
                # Underload situation
                if node.underloaded:
                    print 'Underload...'
                    self.migration_trigger(False, nodes, node, k, sleep_time, time_now)
            except StopIteration: pass
            
