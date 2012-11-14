import time

class ActiveServerInfo(object):
    def __init__(self, timestamp, servercount):
        self.timestamp = timestamp
        self.servercount = servercount


class Scoreboard(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Scoreboard, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    
    active_server_infos = []
    start_timestamp = 0
    
    def __init__(self):
        self.start_timestamp = time.time()
    
    def add_active_info(self, servercount):
        timestamp = time.time()
        Scoreboard.active_server_infos.append(ActiveServerInfo(timestamp, servercount))


    def analytics_average_server_count(self):
        if not self.active_server_infos:
            return 0  
        
        wrapped_infos = []
        wrapped_infos.extend(self.active_server_infos)
        wrapped_infos.append(ActiveServerInfo(time.time(), self.active_server_infos[-1].servercount))
        
        last_info = None
        server_seconds = 0
        total_time = 0
        for info in self.active_server_infos:
            if last_info == None:
                last_info = info
                continue
            
            delta_time = info.timestamp - last_info.timestamp
            servers = last_info.servercount
            server_seconds += (servers * delta_time)
            total_time += delta_time
            
        if total_time == 0:
            return 0 
        
        avg_count = server_seconds / total_time
        print avg_count 
        return avg_count
             
    
    def dump(self):
        print 'Records %i' % len(Scoreboard.active_server_infos)
        print 'Average server count %f' % self.analytics_average_server_count()
        
        
        
        
         