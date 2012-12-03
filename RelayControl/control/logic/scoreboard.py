# Recorded whenever the number of active servers changes
class ActiveServerInfo(object):
    def __init__(self, timestamp, servercount):
        self.timestamp = timestamp
        self.servercount = servercount


# Scoreboard is a singleton class which overrides the new operator
class Scoreboard(object):
    # Singleton construction by overriding new operation
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Scoreboard, cls).__new__(cls, *args, **kwargs)
            cls._instance.flush()
        return cls._instance
    
    def flush(self):
        self.closed = False
        self.start_timestamp = 0
        
        self.active_server_infos = []
        self.cpu_violations = 0
        self.cpu_accumulated = 0
        
        self.imbalance_migrations = 0
        self.overload_migrations = 0
        self.underload_migrations = 0
        self.swaps = 0
    
    def close(self):
        self.closed = True
    
    def add_migration_type(self, migration_type):
        if migration_type == 'Imbalance':
            self.imbalance_migrations += 1
            return
        if migration_type == 'Overload (Empty=False)':
            self.overload_migrations +=1
            return
        if migration_type == 'Overload (Empty=True)':
            self.overload_migrations +=1
            return
        if migration_type == 'Underload (Empty=False)':
            self.underload_migrations +=1
            return
        if migration_type == 'Underload (Empty=True)':
            self.underload_migrations +=1
            return
        if migration_type == 'Swap Part 1':
            self.swaps +=1           
    
    def add_cpu_violations(self, violations):
        if not self.closed:
            self.cpu_violations += violations
    
    def add_cpu_load(self, load):
        if not self.closed:
            self.cpu_accumulated += load
    
    def add_active_info(self, servercount, timestamp):
        if not self.closed:
            self.active_server_infos.append(ActiveServerInfo(timestamp, servercount))

    def analytics_average_server_count(self, pump):
        if not self.active_server_infos:
            return 0
        
        wrapped_infos = []
        wrapped_infos.extend(self.active_server_infos)
        wrapped_infos.append(ActiveServerInfo(pump.sim_time(), self.active_server_infos[-1].servercount))
        
        last_info = None
        server_seconds = 0
        for info in wrapped_infos:
            if last_info == None:
                last_info = info
                continue
            
            delta_time = info.timestamp - last_info.timestamp
            servers = last_info.servercount
            # print 'servers %f - time %f' % (servers, delta_time)
            server_seconds += (servers * delta_time)
            
            # Update last info
            last_info = info
            
        total_time = wrapped_infos[-1].timestamp - wrapped_infos[0].timestamp
        total_time = max(total_time, 1)
        avg_count = server_seconds / total_time
        return avg_count
       
    def get_results(self, pump):
        return (len(self.active_server_infos), self.analytics_average_server_count(pump), 
                self.cpu_violations, self.cpu_accumulated, self.imbalance_migrations,
                self.overload_migrations, self.underload_migrations, self.swaps)
    
    def get_result_line(self, pump):
        res = self.get_results(pump)
        return '%f \t %f \t %i \t %i \t %i \t %i \t %i \t %i' % res
    
    def dump(self, pump):
        print 'Records %i' % len(self.active_server_infos)
        print 'Average server count %f' % self.analytics_average_server_count(pump)
        
