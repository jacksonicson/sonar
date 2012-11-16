import threading
import time
import configuration

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
        self.start_time = time.time()
        self.speedup = float(configuration.SIM_SPEEDUP)
        
        self.handlers.append(Entry(0, initial_handler, self, *handler_args))
        
    def callLater(self, delay, handler, *data):
        cb_time = self.sim_time() + delay
        entry = Entry(cb_time, handler, *data)
        
        self.handlers.append(entry)
        self.handlers.sort(key=lambda a: a.cb_time)

    def stop(self):
        self.running = False
        
    def sim_time(self):
        delta = time.time() - self.start_time
        return float(delta) * self.speedup
        
    def run(self):
        while self.running and self.handlers:
            entry = self.handlers[0]
            
            sim_time = self.sim_time()
            if sim_time < entry.cb_time:
                delta = (entry.cb_time - sim_time) / self.speedup
#                print 'Sleeping %f' % delta
                time.sleep(delta)
                continue
            else:
                valid = entry.cb_time - sim_time
                if valid > 2: 
                    print 'WARING: SYSTEM OVERLOAD'
                    
                self.handlers.remove(entry)
                entry.call()
            
        print 'Message pump exited'     
            
