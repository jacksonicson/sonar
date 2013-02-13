'''
Java is used to get the length of all log messages stored in sonar. The length of
each log message is stored in a txt file. This file gets read by this script which then
calculates some descriptive statistic metrics about the log message length. 
'''

import numpy as np


##########################
## Configuration        ##
##########################
FILE = 'C:/tmep/msgs.txt'
##########################

arr = np.genfromtxt(FILE, delimiter=',')
time = arr[:,0]
pre = time[0]
time[0] = 0
for i in xrange(1, len(time)):
    delta = time[i] - pre
    pre = time[i]
    time[i] = delta

print 'time mean: %f' % np.mean(time)
print 'time std dev: %f' % np.std(time)

import matplotlib.pyplot as plt
print time
bins = np.linspace(0, 10000, 100)
n, bins, patches = plt.hist(time, bins)
plt.show()

#from scipy.cluster.vq import kmeans
#centroids , variance = kmeans(time, 400)
#print centroids

arr = arr[:,1]
print 'max: %f' % np.max(arr)
print 'min: %f' % np.min(arr)
print 'mean: %f' % np.mean(arr)
print 'std dev: %f' % np.std(arr)
print '90 percentile: %f' % np.percentile(arr, 90)
print '50 percentile: %f' % np.percentile(arr, 50)
print '10 percentile: %f' % np.percentile(arr, 10)

import matplotlib.pyplot as plt
f = arr > 0
arr = arr[f]
arr = np.log(arr)
from scipy.stats import gaussian_kde
#n, bins, patches = plt.hist(arr, 50, facecolor='g', alpha=0.75) 

density = gaussian_kde(arr)
xs = np.linspace(0,8,200)
density.covariance_factor = lambda : .25
density._compute_covariance()
plt.plot(xs,density(xs))
plt.show()

hist = np.histogram(arr, 50)
print hist