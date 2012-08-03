from service import times_client

connection = times_client.connect()

result = connection.find('^.*retail.*HWORDER\Z')
for i in result:
    print i
    ts = connection.load(i)
    print ts.frequency
    print ts.name
    print ts.elements
    

times_client.close()