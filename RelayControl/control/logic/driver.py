from collector import ttypes
from threading import Thread
import control.domains as domains
import sys
import time
import configuration
from workload import util as wutil
from service import times_client
import util
from virtual import nodes
import numpy as np

class Driver(Thread):
    
    # The default settings are estimations of the real world infrastructure
    def __init__(self, model, handler, report_rate=3, resize=1):
        super(Driver, self).__init__()

        # Reference to the data model which stores the current infrastructure status
        # Time series are attached to the model        
        self.model = model
        
        # Callback handler to deliver time series readings
        self.handler = handler
        
        # Thread running
        self.running = True
        
        # acceleration * real_time_delta (simulation time runs faster/slower by factor acceleration)
        self.acceleration = float(configuration.SIM_SPEEDUP)
        
        # report rate in real time (e.g. every 3 seconds a value is reported) 
        self.report_rate = float(report_rate) / self.acceleration
        
        # CPU consumption of all domains is divided by this factor
        self.resize = float(resize)
        
        
    def stop(self):
        self.running = False
     
    def is_running(self):
        return self.running
     
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
        print 'Connecting with Times'
        connection = times_client.connect()
        
        min_ts_length = sys.maxint # Minimum length across all TS
        freq = 0 # Frequency of the TS from Times 
        sim_time = 0 # Simulation time (update speed depends on speedup)
        
        # Iterate over all domains and assign them a TS
        for domain in self.model.get_hosts(self.model.types.DOMAIN):
            # Select and load TS (based on the configuration)
            load = domains.cpu_profile_by_name(domain.name)
            print 'loading service: %s ...' % (load)
            ts = connection.load(load)
            
            # Convert TS to a numpy array
            # select TS not time index
            freq = ts.frequency
            ts = wutil.to_array(ts)[1]
            
            # Attach TS to domain 
            domain.ts = ts
            
            # Update max length
            min_ts_length = min(min_ts_length, len(ts))
        
        # Close times connection
        times_client.close()
        
        # Reduce length of time series to 6 hours
        freq = freq / (24.0 / 6.0)
        
        ###############################
        ## Simulation Loop
        ###############################
        # Replay time series data
        while self.running:
            # Index for simulation time 
            tindex = (sim_time / freq)
            if tindex > min_ts_length:
                print 'Driver exited!'
                self.running = False 
                break
            
            # print 'Progress: %f' % ((tindex / min_ts_length) * 100)
            
            # For all nodes update their domains and aggregate the load for the node
            for host in self.model.get_hosts(self.model.types.NODE):
                aggregated_load = 0
                
                # Go over all domains and update their load by their TS
                for domain in host.domains.values():
                    load = np.mean(domain.ts[tindex - 1 : tindex+1]) * self.resize
                    # load = domain.ts[tindex] * self.resize
                     
                    self.__notify(sim_time, domain.name, 'psutilcpu', load)
                    
                    # Load aggregation for the node
                    aggregated_load += (load / (nodes.NODE_CPU_CORES / nodes.DOMAIN_CPU_CORES))


                # Send aggregated load
                self.__notify(sim_time, host.name, 'psutilcpu', aggregated_load * 1 + 15)
            
            # report_rate = report_rate / acceleration
            # sim_time is increased by original report_rate!
            # time passes faster as querying and sleep is reduced! 
            sim_time += self.report_rate * self.acceleration
            
            # Sleep is report_rate / acceleration shorter
            # Whole simulation is accelerated 
            time.sleep(self.report_rate)
            util.sim_time = sim_time
            
