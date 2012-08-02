from configuration import storage
from proto import trace_pb2
from scipy import *
from scipy.signal import *
import array
import csv
import gridfs
import math
import matplotlib.pyplot as plt
import numpy as np
import os
import pymongo
import random
import scipy.stats as stats
import signal



import numpy as np
import scikits.statsmodels.api as sm
import scikits.statsmodels.tsa as tsa
import matplotlib.pyplot as plt


def load_trace(filename):
    fs = gridfs.GridFS(storage.db, collection='tracefiles')
    
    # Check if this file exists already
    if fs.exists(filename=filename) == False:
        return 
    
    gfile = fs.get_last_version(filename=filename)
    
    trace = trace_pb2.Trace()
    trace.ParseFromString(gfile.read())
    return trace


trace = load_trace('/O2 RAW business/3')
ar_trace = []
for element in trace.elements:
    ar_trace.append(element.value) 

data = np.array(ar_trace)




model = tsa.ar_model.AR(data)

fitted = model.fit(maxlag = 20)
print fitted.params


arr = fitted.model.predict(n=1000)

plt.plot(range(len(data)), data)
plt.plot(range(len(arr)), arr)
plt.show()