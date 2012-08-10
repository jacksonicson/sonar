from service import times_client
import matplotlib.pyplot as plt
connection = times_client.connect()

items = connection.find('SIS.*')
for item in items:
    print item

ts = connection.load("SIS_221_cpu_profile")
ff= []
for i in ts.elements:
    ff.append(i.value)

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(range(0, len(ff)), ff)

# ax.acorr(load, maxlags=700)

plt.show()

# ts = connection.load("SIS_194_cpu_profile_profile")
# print ts
#result = connection.find('^SIS_194_cpu_profile_profile')
#timestamp = None
#print 'Starting...'
#for ts in result:
#    ts = connection.load(ts)
#    print len(ts.elements)
    

times_client.close()


# Playing around with numpy
#import numpy
#a = numpy.arange(3) ** 2
#b = numpy.arange(3) ** 3
#c = a + b
#print c
#print c.dtype
#print c.shape
#
#a = numpy.arange(6)
#print a.dtype
#print a.shape
#    
#print 'reshape the array'
#a = a.reshape(2,3)
#print a.dtype
#print a.shape
#print a
#print a[1,1:]
#
#a = numpy.arange(6, dtype=numpy.uint32)
#print a.dtype
#print a.dtype.byteorder
#print a.dtype.itemsize # size in bytes
#
#print numpy.mean(a)
#print numpy.median(a)
#print numpy.average(a, weights=numpy.zeros(6) + 2)
#print numpy.msort(a)
#print numpy.var(a)
## b = numpy.diff(a) / a[:-1]
#b = numpy.diff( numpy.log(a))
#print b
#print numpy.where(a < 3)
