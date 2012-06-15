

def self_monitoring(client, s):
    ids = ttypes.Identifier();
    ids.timestamp = int(time.time())
    ids.sensor = 'sensorhub'
    ids.hostname = HOSTNAME 

    value = ttypes.MetricReading();
    value.value = 1
    value.labels = []
    
    client.logMetric(ids, value)
    
    ids.timestamp = ids.timestamp + 1
    value.value = 0
    client.logMetric(ids, value)
    
    s.enter(5, 1, self_monitoring, (client, s))