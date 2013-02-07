from balancer import strategy
from virtual import placement
from logs import sonarlog
from virtual import nodes
import configuration_advanced
import strategy_imbalance
import strategy_reactive
import strategy_swap
from balancer import migration_queue
import json

# Setup logging
logger = sonarlog.getLogger('controller')

class Strategy(strategy.StrategyBase):
    
    def __init__(self, scoreboard, pump, model):
        super(Strategy, self).__init__(scoreboard, pump, model, configuration_advanced.INTERVAL, configuration_advanced.START_WAIT)
        self.migration_scheduler = migration_queue.MigrationQueue(self)
        
        self.controller_handlers = []
        for setting in configuration_advanced.CONTROLLER_SEQ:
            if setting == 'imbalance':
                self.controller_handlers.append(self.imbalance_controller)
            elif setting == 'reactive':
                self.controller_handlers.append(self.reactive_controller)
            elif setting == 'swap':
                self.controller_handlers.append(self.swap_controller)
            
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
            
            # Remove migration from queue
            self.migration_scheduler.finished(success, domain, node_from, node_to)
        else:
            # Remove migration from queue
            self.migration_scheduler.finished(success, domain, node_from, node_to)

            time_now = self.pump.sim_time()
            node_from.blocked = time_now
            node_to.blocked = time_now
        
    def dump(self):
        print 'Dump Sandpiper controller configuration...'
        logger.info('Strategy Configuration: %s' % json.dumps({'name' : 'Sandpiper',
                                                                 'start_wait' : configuration_advanced.START_WAIT,
                                                                 'interval' : configuration_advanced.INTERVAL,
                                                                 'threshold_overload' : configuration_advanced.THRESHOLD_OVERLOAD,
                                                                 'threshold_underload' : configuration_advanced.THRESHOLD_UNDERLOAD,
                                                                 'percentile' : configuration_advanced.PERCENTILE,
                                                                 'k_value' : configuration_advanced.K_VALUE,
                                                                 'm_value' : configuration_advanced.M_VALUE
                                                                 }))    
    
    def balance(self):
        sleep_time = 60
        time_now = self.pump.sim_time()
        
        for handler in self.controller_handlers:
            migration_triggered = handler(time_now, sleep_time)
            if migration_triggered: 
                return

    def imbalance_controller(self, time_now, sleep_time):
        imbalance_controller = strategy_imbalance.Imbalance(self.model, self.migration_scheduler)
        return imbalance_controller.migrate_imbalance(time_now, sleep_time)
    
    def reactive_controller(self, time_now, sleep_time):
        reactive_controller = strategy_reactive.Reactive(self.model, self.migration_scheduler)
        return reactive_controller.migrate_reactive(time_now, sleep_time)
        
    def swap_controller(self, time_now, sleep_time):
        swap_controller = strategy_swap.Swap(self.model, self.migration_scheduler)
        return swap_controller.migrate_swap(time_now, sleep_time)
