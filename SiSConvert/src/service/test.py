from service import times_client

#connection = times_client.connect()
#
#result = connection.find('^O2.*\Z')
#timestamp = None
#print 'Starting...'
#for ts in result:
#    ts = connection.load(ts)
#    print ts
#    
#    test = ts.elements[0].timestamp
#    if timestamp == None:
#        timestamp = test
#        print timestamp
#    elif timestamp != test:
#        print 'ERRROR in %s' % (ts.name)
#
# times_client.close()


# Playing around with numpy
import numpy
a = numpy.arange(3) ** 2
b = numpy.arange(3) ** 3
c = a + b
print c
print c.dtype
print c.shape

a = numpy.arange(6)
print a.dtype
print a.shape
    
print 'reshape the array'
a = a.reshape(2,3)
print a.dtype
print a.shape
print a
print a[1,1:]

a = numpy.arange(6, dtype=numpy.uint32)
print a.dtype
print a.dtype.byteorder
print a.dtype.itemsize # size in bytes

print numpy.mean(a)
print numpy.median(a)
print numpy.average(a, weights=numpy.zeros(6) + 2)
print numpy.msort(a)
print numpy.var(a)
# b = numpy.diff(a) / a[:-1]
b = numpy.diff( numpy.log(a))
print b
print numpy.where(a < 3)
