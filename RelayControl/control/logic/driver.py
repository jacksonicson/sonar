from collector import ttypes
from threading import Thread
import control.domains as domains
import sys
import time

class Driver(Thread):
    
    def __init__(self, model, handler, report_rate=3, acceleration=25):
        super(Driver, self).__init__()
        
        self.model = model
        self.handler = handler
        self.running = True
        
        # acceleration * real_time_delta (simulation time runs faster/slower by factor acceleration)
        self.acceleration = acceleration  
        
        # report rate in real time (e.g. every 3 seconds a value is reported) 
        self.report_rate = report_rate 
        
    def stop(self):
        self.running = False
     
    def notify(self, timestamp, name, sensor, value):
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
        # Use the existing profiles to load TSD from Times
        from workload import profiles, util
        from service import times_client
        
        print 'Connecting with Times'
        connection = times_client.connect()
        
        min_ts_length = sys.maxint
        freq = 0
        sim_time = 0 # simulation time
        
        # Iterate over all domains and assign them a TS
        for domain in self.model.get_hosts(self.model.types.DOMAIN):
            # Select and load TS (based on the configuration)
            service_name = domains.profile_by_name(domain.name)
            load = service_name + profiles.POSTFIX_NORM
            print 'loading service: %s ...' % (load)
            ts = connection.load(load)
            
            # Convert TS to a numpy array
            # select TS not time index
            freq = ts.frequency
            ts = util.to_array(ts)[1]
            
            # Attach TS to domain 
            domain.ts = ts
            
            # Update max length
            min_ts_length = min(min_ts_length, len(ts))
        
        # Replay time series data
        while self.running:
            # Simulation simulation_time 
            tindex = (sim_time / freq) % min_ts_length
            # print 'TS index: %i' % tindex
            
            # For all nodes update their domains and aggregate the load for the node
            for host in self.model.get_hosts(self.model.types.NODE):
                aggregated_load = 0
                
                # Go over all domains and update their load by their TS
                for domain in host.domains.values():
                    load = domain.ts[tindex]
                     
                    self.notify(sim_time, domain.name, 'psutilcpu', load)
                    
                    # Load aggregation for the node
                    aggregated_load += load


                # Send aggregated load
                self.notify(sim_time, host.name, 'psutilcpu', aggregated_load)
            
            # Simulation sleep
            sim_time += self.report_rate * self.acceleration
            time.sleep(self.report_rate)
            
            
