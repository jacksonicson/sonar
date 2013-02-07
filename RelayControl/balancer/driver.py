from collector import ttypes
from control import domains
from service import times_client
from virtual import nodes
from workload import profiles, util as wutil
from workload.profiles import RAMP_UP
from workload.timeutil import *  # @UnusedWildImport
import numpy as np
import sys

##########################
# # CONFIGURATION        ##
BASE_LOAD = 0

NOISE = False
NOISE_MEAN = 0.0
NOISE_SIGMA = 1.0

MIGRATION_SOURCE = 13 
MIGRATION_TARGET = 17
##########################

class Driver:
    
    # The default settings are estimations of the real world infrastructure
    def __init__(self, scoreboard, pump, model, handler, report_rate=3):
        # Reference to scoreboard
        self.scoreboard = scoreboard 
        
        # Reference to the message pump
        self.pump = pump

        # Reference to the data model which stores the current infrastructure status
        # Time series are attached to the model        
        self.model = model
        
        # Callback handler to deliver time series readings
        self.handler = handler
        
        # report rate in real time (e.g. every 3 seconds a value is reported) 
        self.report_rate = float(report_rate)
        
        
    def start(self):
        print 'Connecting with Times'
        connection = times_client.connect()
        
        self.min_ts_length = sys.maxint  # Minimum length across all TS
        ts_freq = 0  # Frequency of the TS from Times
        
        # Iterate over all domains and assign them a TS
        for domain in self.model.get_hosts(self.model.types.DOMAIN):
            # Select and load TS (based on the configuration)
            index = domains.index_of(domain.name)
            mapping = domains.domain_profile_mapping[index]
            load = profiles.get_cpu_profile_for_initial_placement(mapping.profileId)
            
            ts = connection.load(load)
            
            # Convert TS to a numpy array
            # select TS not time index
            ts_freq = ts.frequency
            ts = wutil.to_array(ts)[1]
            
            # Add noise to the time series
            if NOISE:
                # random = np.random.lognormal(mean=NOISE_MEAN, sigma=NOISE_SIGMA, size=len(ts))
                random = np.random.normal(loc=NOISE_MEAN, scale=NOISE_SIGMA, size=len(ts))
                ts += random
                ts[ts > 100] = 100
                ts[ts < 0] = 0
            
            # Attach TS to domain 
            domain.ts = ts
            
            # Update max length
            self.min_ts_length = min(self.min_ts_length, len(ts))
        
        # Close times connection
        times_client.close()
        
        # Reduce length of time series to 6 hours
        # Calculation: Adjust frequency by (new duration / current TS duration)
        self.freq = ts_freq * (profiles.EXPERIMENT_DURATION / (self.min_ts_length * ts_freq))
        
        # Calculate ramp up delete time
        self.ramp_up = profiles.RAMP_UP
        self.ramp_down = profiles.RAMP_DOWN
        
        # Schedule message pump
        self.pump.callLater(0, self.run)
     
     
    def __notify(self, timestamp, name, sensor, value):
        data = ttypes.NotificationData()
        data.id = ttypes.Identifier()  
        data.id.hostname = name
        data.id.sensor = sensor
        data.id.timestamp = timestamp
        
        data.reading = ttypes.MetricReading()
        data.reading.value = value
        data.reading.labels = []
        
        self.handler.receive([data, ])
     
    def run(self):
        # Index for simulation time
        sim_time = self.pump.sim_time() 
        tindex = (sim_time + self.ramp_up) / self.freq
        if tindex >= (self.min_ts_length - self.ramp_down / self.freq):
            print 'Driver exited!'
            print 'Shutting down simulation...'
            self.scoreboard.Scoreboard().close() 
            self.pump.stop()
            return
        
        # Update slot count in scoreboard
        self.scoreboard.Scoreboard().update_slot_count()
        
        # For all nodes update their domains and aggregate the load for the node
        for host in self.model.get_hosts(self.model.types.NODE):
            # Reset aggregated server load
            aggregated_load = 0
            
            # Go over all domains and update their load by their TS
            for domain in host.domains.values():
                load = domain.ts[tindex]
                 
                # Notify load to the domain
                self.__notify(sim_time, domain.name, 'psutilcpu', load)
                
                # Load aggregation for the node
                aggregated_load += nodes.to_node_load(load)
                                
                # Update aggregated cpu load
                self.scoreboard.Scoreboard().add_cpu_load(load)

            # Add hypervisor load to the aggregated load
            # For the SSAPv this causes service level violations
            aggregated_load += BASE_LOAD
            
            # Add Migration overheads
            if host.active_migrations_out: 
                aggregated_load += host.active_migrations_out * MIGRATION_SOURCE
            
            if host.active_migrations_in:
                aggregated_load += host.active_migrations_in * MIGRATION_TARGET 
            
            self.__notify(sim_time, host.name, 'psutilcpu', aggregated_load)
            
            # Update overload counter
            if aggregated_load > 100:
                self.scoreboard.Scoreboard().add_cpu_violations(1)
                
        
        # Schedule next call for run
        self.pump.callLater(self.report_rate, self.run) 
            
