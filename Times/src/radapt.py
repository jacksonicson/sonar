from service import times_client
import sys

'''
Example usage for this in an R script: 
data = read.csv(pipe('python D:/work/dev/sonar/sonar/Times/src/radapt.py SIS_142_cpu'))
'''

if len(sys.argv) != 2:
    print 'Wrong number of arguments!'
    sys.exit(1)

try:
    connection = times_client.connect()
    name = sys.argv[1]
    
    result = connection.find(name)
    if len(result) == 0:
        print 'No TS found with name: %s' %name
        sys.exit(1)
        
    ts = connection.load(name)
    for element in ts.elements:
        print '%i,%i' % (element.timestamp / 1000, element.value)
    
finally:
    times_client.close()