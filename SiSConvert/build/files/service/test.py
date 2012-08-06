from service import times_client

connection = times_client.connect()

result = connection.find('^O2.*\Z')
timestamp = None
print 'Starting...'
for ts in result:
    ts = connection.load(ts)
    print ts
    
    test = ts.elements[0].timestamp
    if timestamp == None:
        timestamp = test
        print timestamp
    elif timestamp != test:
        print 'ERRROR in %s' % (ts.name)

    

times_client.close()
