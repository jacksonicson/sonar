from proto import trace_pb2
import configuration.storage as storage
import csv
import gridfs
import os
 
def load_trace(path, identifier, number):
    file = open(path, 'r')
    reader = csv.reader(file)
    
    fs = gridfs.GridFS(storage.db, collection='tracefiles')
    
    filename = "/" + identifier + "/" + number
    
    # Check if this file exists already
    if fs.exists(filename=filename):
        print 'removing existing file %s ' % (filename) 
        to_del = fs.get_last_version(filename=filename)
        fs.delete(to_del._id)
     
    # Create and fill file
    gfile = fs.new_file(filename=filename)
    try:
        trace = trace_pb2.Trace()
        trace.name = filename

        reader.next()        
        for str in reader:
            element = trace.elements.add()
            element.start = int(str[1])
            element.stop = int(str[2])
            element.value = int(str[3])
            
        gfile.write(trace.SerializeToString())
        
    finally:
        gfile.close()
        
    id = gfile._id
    create_timeseries(filename, id)
    
    return id
        
    
if __name__ == '__main__':

    # Configuration #############
    # The directory with the CSV files (SIS format: Start, End, Value)
    directory_elements = ['D:/', 'work', 'data', 'SIS time series 2']
    directory = ''
    for element in directory_elements:
        directory = os.path.join(directory, element)
    # ###########################

    # subdirectory which contains the RAW CSV file
    subpath_elements = ['1', 'raw', 'series.csv']

    # iterate over all directory and import the RAW CSV files
    dataset = os.listdir(directory)
    for timeseries_number in dataset:
        if os.path.isfile(timeseries_number):
            continue
        elif str.startswith(timeseries_number, '.'):
            continue
        
        path = os.path.join(directory, timeseries_number)
        
        for element in subpath_elements: 
            path = os.path.join(path, element)
        
        print path
        load_trace(path, 'SIS RAW', timeseries_number)

    print 'done'
