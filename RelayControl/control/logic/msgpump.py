import configuration
import threading
import time

class Entry:
    def __init__(self, cb_time, handler, *args):
        self.cb_time = float(cb_time)
        self.handler = handler
        self.args = args
        
    def call(self):
        self.handler(*self.args)
    
class Pump(threading.Thread):
    def __init__(self, initial_handler, *handler_args):
        # Thread init method
        super(Pump, self).__init__()
        
        self.running = True
        self.handlers = []
        self.production = configuration.PRODUCTION
        self.start_time = time.time() if self.production else 0
        self.speedup = float(configuration.PUMP_SPEEDUP)
        
        self.handlers.append(Entry(0, initial_handler, self, *handler_args))
        
    def callLater(self, delay, handler, *data):
        cb_time = self.sim_time() + delay
        entry = Entry(cb_time, handler, *data)
        
        self.handlers.append(entry)
        self.handlers.sort(key=lambda a: a.cb_time)

    def stop(self):
        self.running = False
        
    def sim_time(self):
        if self.production: 
            return time.time()
    
        return self.start_time
        
    def run(self):
        while self.running and self.handlers:
            entry = self.handlers[0]
            
            sim_time = self.sim_time()
            if sim_time < entry.cb_time:
                if self.production:
                    delta = (entry.cb_time - sim_time) / self.speedup
                    time.sleep(delta)
                else:
                    self.start_time = entry.cb_time
                    
                continue
            else:
                valid = entry.cb_time - sim_time
                if valid > 2: 
                    print 'WARING: SYSTEM OVERLOAD'
                    
                self.handlers.remove(entry)
                entry.call()
                
        print 'Message pump exited'     
            
