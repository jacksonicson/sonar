from service import times_client
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
    
    # 5 minutes monitoring frequency
    filename_cpu = identifier + '_' + number + '_cpu'
    connection.create(filename_cpu, 60 * 5 * 1000)
    filename_mem = identifier + '_' + number + '_mem'
    connection.create(filename_mem, 60 * 5 * 1000)
     
    # Skip the first line
    reader.next()        
    
    ts_cpu_elements = []
    ts_mem_elements = []
    for line in reader:
        element = ttypes.Element()
        element.timestamp = long(line[1])
        element.value = int(line[3])
        ts_cpu_elements.append(element)
        
        element = ttypes.Element()
        element.timestamp = long(line[1])
        element.value = int(line[4])
        ts_mem_elements.append(element)
    
    connection.append(filename_cpu, ts_cpu_elements)
    connection.append(filename_mem, ts_mem_elements)
    
    
if __name__ == '__main__':
    global connection
    connection = times_client.connect()

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
    times_client.close()
