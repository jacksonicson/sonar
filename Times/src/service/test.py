from numpy import *
from os import listdir
from service import times_client
import dtw
import math
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import mlpy
import operator

connection = times_client.connect()


def print_matrix(matrix):
    for i in xrange(0, len(matrix)):
        row = matrix[i]
        for j in xrange(0, len(row)):
            print '%03d' % row[j],
        
        print ''

def classify0(inX, dataSet, labels, k):
    dataSetSize = dataSet.shape[0]
    diffMat = tile(inX, (dataSetSize,1)) - dataSet
    sqDiffMat = diffMat**2
    sqDistances = sqDiffMat.sum(axis=1)
    distances = sqDistances**0.5
    sortedDistIndicies = distances.argsort()     
    classCount={}          
    for i in range(k):
        voteIlabel = labels[sortedDistIndicies[i]]
        classCount[voteIlabel] = classCount.get(voteIlabel,0) + 1
    sortedClassCount = sorted(classCount.iteritems(), key=operator.itemgetter(1), reverse=True)
    return sortedClassCount[0][0]


def dtw(a, b, d=lambda x, y : abs(x - y)):
    rows = len(a)
    cols = len(b)
    matrix = [[0 for _ in xrange(cols)] for _ in xrange(rows)]
    
    # Apply global constraint
    t = 3
    for i in xrange(0, rows):
        middle = i
        for j in xrange(0, cols):
            if j < (middle - t):
                matrix[i][j] = 99
            elif j > (middle + t):
                matrix[i][j] = 99
        
      
    matrix[0][0] = d(a[0], b[0])
    for i in xrange(1, rows):
        if matrix[i][0] > 0:
            break
        matrix[i][0] = matrix[i - 1][0] + d(a[i], b[0])

    for j in xrange(1, cols):
        if matrix[0][j] > 0:
            break
        matrix[0][j] = matrix[0][j - 1] + d(a[0], b[j])
      
    for i in xrange(1, rows):
        for j in xrange(1, cols):
            if matrix[i][j] > 0:
                continue 
            choices = matrix[i - 1][j], matrix[i][j - 1], matrix[i - 1][j - 1]
            matrix[i][j] = min(choices) + d(a[i], b[j])

    print_matrix(matrix)
    return matrix[rows-1][cols-1]
    

def dynamicTimeWarp(seqA, seqB, d=lambda x, y: abs(x - y)):
    # create the cost matrix
    numRows, numCols = len(seqA), len(seqB)
    cost = [[0 for _ in range(numCols)] for _ in range(numRows)]
    
    # initialize the first row and column
    cost[0][0] = d(seqA[0], seqB[0])
    for i in xrange(1, numRows):
        cost[i][0] = cost[i - 1][0] + d(seqA[i], seqB[0])

    for j in xrange(1, numCols):
        cost[0][j] = cost[0][j - 1] + d(seqA[0], seqB[j])

    # fill in the rest of the matrix
    for i in xrange(1, numRows):
        for j in xrange(1, numCols):
            
            choices = cost[i - 1][j], cost[i][j - 1], cost[i - 1][j - 1]
            cost[i][j] = min(choices) + d(seqA[i], seqB[j])

    for row in cost:
        for entry in row:
            print "%03d" % entry,
        print ""
    return cost[-1][-1]


items = connection.find('SIS.*')
for item in items:
    pass # print item

ts = connection.load("SIS_221_cpu_profile")
ff = []
for i in ts.elements:
    ff.append(i.value)

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(range(0, len(ff)), ff)

# ax.acorr(load, maxlags=700)

x = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 5, 5, 0]
y = [0, 0, 0, 0, 0, 0, 0, 5, 5, 5, 0, 0, 0, 0, 0]


# print dynamicTimeWarp(x,y)
print dtw(x, y)

#fig = plt.figure(1)
#ax = fig.add_subplot(111)
#plot1 = plt.imshow(cost.T, origin='lower', cmap=cm.gray, interpolation='nearest')
#plot2 = plt.plot(path[0], path[1], 'w')
#xlim = ax.set_xlim((-0.5, cost.shape[0]-0.5))
#ylim = ax.set_ylim((-0.5, cost.shape[1]-0.5))
#plt.show()



# plt.show()

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
