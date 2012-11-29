from logs import sonarlog
import controller
import json
from control.logic import scoreboard


######################
## CONFIGURATION    ##
######################
START_WAIT = 120
INTERVAL = 10*60
######################

# Setup logging
logger = sonarlog.getLogger('controller')

class DSAP(controller.LoadBalancer):
    
    def __init__(self, pump, model):
        super(DSAP, self).__init__(pump, model, INTERVAL, START_WAIT)
        print "INIT DSAP"
        self.var = []
        
        # initial placement via SSAP        TODO
        
        # migrationen schedulen via migration list (later with manager)
        
        
        # aktuelle zeit
        time_now = self.pump.sim_time() 

#        self.migrate(domain, source, target, k)        # TODO laeuft parallel >> später queue 

        
        
    def dump(self):
        print 'Dump DSAP controller configuration...'
        logger.info('Controller Configuration: %s' % json.dumps({'name' : 'DSAP-Controller',
                                                                 'start_wait' : START_WAIT,
                                                                 'interval' : INTERVAL,
                                                                 }))
    
    def balance(self):
        print 'DSAP-Controller'
        ############################################
        ## HOTSPOT DETECTOR ########################
        ############################################
        k = 40
        self.check_hotspots(k)
        
        #        check # of hotspots >> call DSAP.py / Gurobi
        scoreboard.Scoreboard();
        self.pump.sim_time();   # aktuelle Zeit
 
#        determine whether node is OVERLOADED or UNDERLOADED
        
        ############################################
        ## MIGRATION MANAGER #######################
        ############################################
        # Calculate volumes of each node
        nodes = []
        domains = []

#        re-schedule VMs 
        
        
        ############################################
        ## TRIGGER MIGRATIONS ######################
        ############################################

#        time_now = self.pump.sim_time()
#        sleep_time = 60


        for node in nodes:
            node.dump()

#            TODO: handle OVERLOAD + IMBALANCE situations

            try:
                # Overload situation
                if node.overloaded:
                    print 'Overload...'
#                    self.migration_trigger(True, nodes, node, k, sleep_time, time_now)
#                    bzw direkt über (ohne zusätzlicher Fkt)
                    self.migrate(domain, source, target, k)
            except StopIteration: pass 


#        re-schedule VMs
        
        
        
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
    
