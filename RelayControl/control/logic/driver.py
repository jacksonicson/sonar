from collector import ttypes
import control.domains as domains
import sys
from workload import util as wutil
from service import times_client
from virtual import nodes
import numpy as np
import configuration
import scoreboard

class Driver:
    
    # The default settings are estimations of the real world infrastructure
    def __init__(self, pump, model, handler, report_rate=3, resize=1):
        # Reference to the message pump
        self.pump = pump

        # Reference to the data model which stores the current infrastructure status
        # Time series are attached to the model        
        self.model = model
        
        # Callback handler to deliver time series readings
        self.handler = handler
        
        # Thread running
        self.running = True
        
        # report rate in real time (e.g. every 3 seconds a value is reported) 
        self.report_rate = float(report_rate)
        
        # CPU consumption of all domains is divided by this factor
        self.resize = float(resize)
        
        
    def start(self):
        print 'Connecting with Times'
        connection = times_client.connect()
        
        self.min_ts_length = sys.maxint # Minimum length across all TS
        freq = 0 # Frequency of the TS from Times 
        
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
            self.min_ts_length = min(self.min_ts_length, len(ts))
        
        # Close times connection
        times_client.close()
        
        # Reduce length of time series to 6 hours
        self.freq = freq / (24.0 / 5.0)
        
        # Lognormal noise generator
        self.random = np.random.lognormal(mean=0.0, sigma=1.0, size=10000)
        self.rc = 0
        
        # Schedule message pump
        self.pump.callLater(0, self.run)
     
        # Log TSD
        self.used_tsd = {}
     
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
     
    def to_file(self):
        for domain in self.used_tsd:
            f = open(configuration.path(domain.name), 'w')
            tsd = self.used_tsd[domain]
            for r in tsd:
                f.write(str(r) + '\n')
            f.close()   
        
    def run(self):
        # Index for simulation time
        sim_time = self.pump.sim_time() 
        tindex = (sim_time / self.freq)
        if tindex > self.min_ts_length:
            print 'Driver exited!'
            self.running = False
            self.pump.stop()
            self.to_file() 
            return
        
        # print 'Progress: %f' % ((tindex / min_ts_length) * 100)
        
        # For all nodes update their domains and aggregate the load for the node
        for host in self.model.get_hosts(self.model.types.NODE):
            aggregated_load = 0
            
            # Go over all domains and update their load by their TS
            for domain in host.domains.values():
                load = np.mean(domain.ts[tindex - 2 : tindex]) * self.resize
                # load = domain.ts[tindex] * self.resize
                 
                rc = (self.rc + 1) % 10000
                load += self.random[rc]
                if load < 0: load=0
                if load > 100: load = 100
                 
                if domain not in self.used_tsd: 
                    self.used_tsd[domain] = []
                self.used_tsd[domain].append(load)
                 
                self.__notify(sim_time, domain.name, 'psutilcpu', load)
                
                # Load aggregation for the node
                aggregated_load += (load / (nodes.NODE_CPU_CORES / nodes.DOMAIN_CPU_CORES))


            # Send aggregated load
            self.__notify(sim_time, host.name, 'psutilcpu', aggregated_load + 12)
            
            # Update overload counter
            if (aggregated_load + 12) > 100: 
                scoreboard.Scoreboard().add_cpu_violations(1)
            
        
        # Whole simulation might run accelerated
        self.pump.callLater(self.report_rate, self.run) 
            
