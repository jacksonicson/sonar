from collector import ttypes
from threading import Thread
import time

class Driver(Thread):
        
    def __init__(self, model, handler):
        self.model = model
        self.handler= handler
        
    def run(self):
        # Use the existing profiles to load TSD from Times
        from workload import profiles, util
        from service import times_client
        
        print 'Connecting with Times'
        connection = times_client.connect()
        
        i = 0
        length = 0
        for host in self.model.get_hosts():
            if host.type != self.model.types.DOMAIN:
                continue
           
            service = profiles.selected[i]
            i += 1
            
            load = service.name + profiles.POSTFIX_NORM
            print 'loading service: %s ...' % (load)
            ts = connection.load(load)
            ts = util.to_array(ts)[1] # only load time
            host.ts = ts
            length = max(length, len(ts))
        
        # Simulate time steps
        while True: 
            for tindex in xrange(length):
                for host in self.model.get_hosts():
                    if host.type != self.model.types.NODE:
                        continue
                    
                    aggregated_load = 0
                    for domain in host.domains.values():
                        load = domain.ts[tindex]
                        aggregated_load += load 
                    
                        data = ttypes.NotificationData()
                        data.id = ttypes.Identifier()  
                        data.id.hostname = domain.name
                        data.id.sensor = 'psutilcpu'
                        data.id.timestamp = tindex
                        
                        data.reading = ttypes.MetricReading()
                        data.reading.value = load
                        data.reading.labels = []
                        
                        self.handler.receive(data)
                        
                    # print 'aggregated: %s = %f' % (host.name, aggregated_load)
                    data = ttypes.NotificationData()
                    data.id = ttypes.Identifier()  
                    data.id.hostname = host.name
                    data.id.sensor = 'psutilcpu'
                    data.id.timestamp = tindex
                    
                    data.reading = ttypes.MetricReading()
                    data.reading.value = aggregated_load
                    data.reading.labels = []
                    
                    self.handler.receive(data) 
                
                time.sleep(1)
            
            print 'NEXT SIMULATION CYCLE #########################################'