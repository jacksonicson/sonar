from service import ctimes

connection = ctimes.connect()

result = connection.find('^.*retail.*HWORDER\Z')
for i in result:
    print i
    ts = connection.load(i)
    print ts.frequency
    print ts.name
    print ts.elements
    

ctimes.close()