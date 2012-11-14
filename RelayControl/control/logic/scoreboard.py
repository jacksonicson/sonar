import util

# Recorded whenever the number of active servers changes
class ActiveServerInfo(object):
    def __init__(self, timestamp, servercount):
        self.timestamp = timestamp
        self.servercount = servercount


class Scoreboard(object):
    # Singleton construction by overriding new operation
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Scoreboard, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    # Scoreboard data
    active_server_infos = []
    start_timestamp = 0
    
    def __init__(self):
        Scoreboard.start_timestamp = util.time()
    
    def add_active_info(self, servercount):
        timestamp = util.time()
        Scoreboard.active_server_infos.append(ActiveServerInfo(timestamp, servercount))

    def analytics_average_server_count(self):
        wrapped_infos = []
        wrapped_infos.extend(Scoreboard.active_server_infos)
        wrapped_infos.append(ActiveServerInfo(util.time(), Scoreboard.active_server_infos[-1].servercount))
        
        last_info = None
        server_seconds = 0
        for info in wrapped_infos:
            if last_info == None:
                last_info = info
                continue
            
            delta_time = info.timestamp - last_info.timestamp
            servers = last_info.servercount
            print 'servers %f - time %f' % (servers, delta_time)
            server_seconds += (servers * delta_time)
            
            # Update last info
            last_info = info
            
        total_time = wrapped_infos[-1].timestamp - wrapped_infos[0].timestamp + 1
        print 'total time %f' % total_time
        avg_count = server_seconds / total_time
        return avg_count
             
    
    def dump(self):
        print 'Records %i' % len(Scoreboard.active_server_infos)
        print 'Average server count %f' % self.analytics_average_server_count()
        
        
        
        
         