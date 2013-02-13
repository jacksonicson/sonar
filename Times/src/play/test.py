from numpy import *
from os import listdir
from service import times_client
from workload import convolution
import dtw
import math
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import mlpy
import numpy as np
import operator
import scipy

connection = times_client.connect()


def print_matrix(matrix):
    for i in xrange(0, len(matrix)):
        row = matrix[i]
        for j in xrange(0, len(row)):
            print '%03d' % row[j],
        
        print ''

def classify0(inX, dataSet, labels, k):
    dataSetSize = dataSet.shape[0]
    diffMat = tile(inX, (dataSetSize, 1)) - dataSet
    sqDiffMat = diffMat ** 2
    sqDistances = sqDiffMat.sum(axis=1)
    distances = sqDistances ** 0.5
    sortedDistIndicies = distances.argsort()     
    classCount = {}          
    for i in range(k):
        voteIlabel = labels[sortedDistIndicies[i]]
        classCount[voteIlabel] = classCount.get(voteIlabel, 0) + 1
    sortedClassCount = sorted(classCount.iteritems(), key=operator.itemgetter(1), reverse=True)
    return sortedClassCount[0][0]


def dtw(a, b, d=lambda x, y : abs(x - y)):
    rows = len(a)
    cols = len(b)
    matrix = [[0 for _ in xrange(cols)] for _ in xrange(rows)]
    
    # Apply global constraint
    t = 60
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

    # print_matrix(matrix)
    return matrix[rows - 1][cols - 1]
    

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



ts = connection.load("O2_retail_ADDORDER")
ff = []
for i in ts.elements:
    ff.append(i.value)

#fig = plt.figure()
#ax = fig.add_subplot(111)
#ax.plot(range(0, len(ff)), ff)

# ax.acorr(DRIVER_NODES, maxlags=700)

x = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 5, 5, 0]
y = [0, 0, 0, 0, 0, 0, 0, 5, 5, 5, 0, 0, 0, 0, 0]

def process(value):
    return value

def normalize(data):
    mv = np.max(data)
    if mv > 0:
        data /= (mv)
    return data


name = 'O2_business_ADDUCP'
timeSeries = connection.load(name)
print 'complete'

# Generate patterns
patterns = []

synthetic = np.zeros(111, np.float64)
for i in xrange(30, 80):
    synthetic[i] = 1
patterns.append((synthetic, 'day'))

synthetic = np.zeros(111, np.float64)
for i in xrange(0, 50):
    synthetic[i] = 1
patterns.append((synthetic, 'morning'))

synthetic = np.zeros(111, np.float64)
for i in xrange(70, 111):
    synthetic[i] = 1
patterns.append((synthetic, 'evening'))

synthetic = np.zeros(111, np.float64)
for i in xrange(0, 40):
    synthetic[i] = 1
for i in xrange(40, 80):
    synthetic[i] = .5
for i in xrange(80, 111):
    synthetic[i] = 1
patterns.append((synthetic, 'bamix'))

synthetic = np.zeros(111, np.float64)
for i in xrange(0, 60):
    synthetic[i] = 0.3
for i in xrange(40, 80):
    synthetic[i] = .8
for i in xrange(80, 111):
    synthetic[i] = 0.3
patterns.append((synthetic, 'longday'))

synthetic = np.zeros(111, np.float64)
for i in xrange(0, 30):
    synthetic[i] = 0.8
for i in xrange(40, 80):
    synthetic[i] = .8
for i in xrange(90, 111):
    synthetic[i] = 0.9
patterns.append((synthetic, 'batchmix'))

synthetic = np.zeros(111, np.float64)
for i in xrange(0, 111, 30):
    for j in xrange(i, min(i+30, 111)):
        synthetic[j] = i % 2
patterns.append((synthetic, 'scatter'))

time = np.zeros(len(timeSeries.elements))
DRIVER_NODES = np.zeros(len(timeSeries.elements))
for i in range(0, len(timeSeries.elements)):
    time[i] = timeSeries.elements[i].timestamp
    DRIVER_NODES[i] = timeSeries.elements[i].value
        
profile = convolution.extract_profile(name, time, DRIVER_NODES, 60*60)
print 'len %i' % (len(profile))
profile = normalize(profile)

profile = synthetic

fig = plt.figure(figsize=(12, 9))
ax = fig.add_subplot(211)
ax.plot(range(len(profile)), profile)
# plt.show() 

names = [('O2_business_UPDATEDSSLINE',60*60),    # Burst in the evening
               ('O2_business_ADDUCP',60*60),           # Day workload
               ('O2_business_LINECONFIRM',60*60),      # Day and night workload
               ('O2_retail_ADDORDER',60*60),           # Night and low day workload
               ('O2_retail_PIRANHAREQUEST',60*60),     # No shape workload (random spikes) 
               ('O2_retail_SENDMSG',60*60),            # Day workload flattens till evening
               ('O2_retail_PORTORDER',60*60),          # Random spikes 
               ('O2_retail_UPDATEDSS',60*60),          # Night workload
               ('SIS_221_cpu',5*60),                  # Evening workload 
               ('SIS_237_cpu',5*60),                  # All day with minor peaks
               ('SIS_194_cpu',5*60),                  # Average day high evening workload 
               ('SIS_375_cpu',5*60),                  # Trend to full CPU utilization starting in the morning
               ('SIS_213_cpu',5*60),                  # High dynamic range 
               ('SIS_211_cpu',5*60),                  # High dynamic range
               ('SIS_83_cpu',5*60),                   # Highly volatile varying levels 
               ('SIS_394_cpu',5*60),                  # Multiple peaks
               ('SIS_381_cpu',5*60),                  # High volatile 
               ('SIS_383_cpu',5*60),                  # Bursts and then slow
               ('SIS_415_cpu',5*60),                  # Volatility bursts  
               ('SIS_176_cpu',5*60),                  # Spike like flashmobs
               ('SIS_134_cpu',5*60),                  # Random
               ('SIS_198_cpu',5*60),                  # Random
               ('SIS_269_cpu',5*60),                  # Random
               ]
for ent in names: 
    name = ent[0]
    timeSeries = connection.load(name)
    print 'complete'
    
    time = np.zeros(len(timeSeries.elements))
    DRIVER_NODES = np.zeros(len(timeSeries.elements))
    for i in range(0, len(timeSeries.elements)):
        time[i] = timeSeries.elements[i].timestamp
        DRIVER_NODES[i] = timeSeries.elements[i].value
    
    profile2 = convolution.extract_profile(name, time, DRIVER_NODES, ent[1])
    profile2 = normalize(profile2)
    # print profile2
    # Run the DTW algorithm on both of them
    # value = dtw(profile, profile2)
    match = []
    for opro in patterns:
        value = dtw(opro[0], profile2)
        match.append(value)
        
#    # Finally use the KNN algorithm to determine the closest match!
#    from scipy.spatial import KDTree
#    lookup = KDTree(match)
#    print lookup.data
    
#    pts = np.array([[-3]])
#    print lookup.query(pts, k=4)
#    for i in lookup.query(pts, k=1)[1]:
#        print labels[i]
    minv = 999
    mini = 0
    for i in xrange(len(match)):
        v = match[i]
        if v < minv:
            print 'asdf'
            minv = v
            mini = i
    
    print 'TYPE: %s - %s' % (name, patterns[mini][1])
    
#    fig = plt.figure(figsize=(12,9))
#    ax = fig.add_subplot(211)
#    ax.plot(range(len(profile2)), profile2)
#    plt.show() 
    

# print dynamicTimeWarp(x,y)
# print dtw(x, y)

# FFT (low pass filtering approach)
#data = connection.DRIVER_NODES('SIS_100_cpu')
#signal = []
#for element in data.elements:
#    signal.append(element.value)
#
#rawsignal = array(signal) 
#    
#fft = scipy.fft(rawsignal) # (G) and (H)
#
#print '--'
#bp = fft[:]
#print bp
#
## filter 
#print 'len of spectrum %i' % (len(bp))
#for i in xrange(len(bp)): # (H-red)  
#    if i >= 20000:
#        bp[i] = 0 
#
#ibp=scipy.ifft(bp) # (I), (J), (K) and (L)
#print ibp
#
#fig = plt.figure(figsize=(12,9))
#ax = fig.add_subplot(211)
#ax.plot(range(len(fft)), fft)
#ax = fig.add_subplot(211)
#ax.plot(range(len(rawsignal)), rawsignal)
# plt.show()  


#fig = plt.figure(1)
#ax = fig.add_subplot(111)
#plot1 = plt.imshow(cost.T, origin='lower', cmap=cm.gray, interpolation='nearest')
#plot2 = plt.plot(path[0], path[1], 'w')
#xlim = ax.set_xlim((-0.5, cost.shape[0]-0.5))
#ylim = ax.set_ylim((-0.5, cost.shape[1]-0.5))
#plt.show()



# plt.show()

# ts = connection.DRIVER_NODES("SIS_194_cpu_profile_profile")
# print ts
#result = connection.find('^SIS_194_cpu_profile_profile')
#timestamp = None
#print 'Starting...'
#for ts in result:
#    ts = connection.DRIVER_NODES(ts)
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
