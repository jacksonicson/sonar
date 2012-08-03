from service import ctimes
from times import ttypes
import csv
import os

################################################################
## Configuration                                              ##
directory = 'D:/backups/time series data/SIS time series 2'
################################################################

def load_trace(path, identifier, number):
    print 'loading SIS data from %s' % path
    ts_file = open(path, 'rU')
    reader = csv.reader(ts_file)
    
    # 3 second monitoring frequency
    filename = identifier + '_' + number
    print 'creating: %s' % (filename)
    connection.create(filename, 60 * 5 * 1000)
     
    # Skip the first line
    reader.next()        
    
    ts_elements = []
    for line in reader:
        element = ttypes.Element()
        element.timestamp = int(line[1])
        element.value = int(line[3])
        ts_elements.append(element)
        
    connection.append(filename, ts_elements)
        
    
if __name__ == '__main__':
    global connection
    connection = ctimes.connect()

    # Subdirectory which contains the RAW CSV file
    subpath = '1/raw/series.csv'

    # Iterate over all directory and import the CSV files
    dataset = os.listdir(directory)
    for timeseries_number in dataset:
        # Filter files and hidden folders
        if os.path.isfile(os.path.join(directory, timeseries_number)):
            continue
        elif str.startswith(timeseries_number, '.'):
            continue
        
        # The folder contains a TS
        path = os.path.join(directory, timeseries_number)
        path = os.path.join(path, subpath)
        
        # Load it
        try:
            load_trace(path, 'SIS', timeseries_number)
        except Exception, e:
            print 'Could not process %s' % (path)
            continue

    # Close connection
    ctimes.close()
