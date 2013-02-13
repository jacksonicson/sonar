import zookeeper
from pykeeper import ZooKeeper, event

def connectWithZooKeeper(sensorHub):
    zk = ZooKeeper('localhost:22182')
    zk.connect()
    
    if zk.exists('/sensors') == None:
        try:
            zk.create('/sensors', '')
        except Exception as e:
            print e
    
    zk.create('/sensor' + HOSTNAME, 'run', flags=zookeeper.EPHEMERAL)
    
    def watcher(event):
        print 'updating configuration...'
        zk.get('/sensor' + HOSTNAME, watcher)
    
    zk.get('/sensor' + HOSTNAME, watcher)
