from proto import trace_pb2
import configuration.storage as storage
import csv
import gridfs
import os

def load_trace(path, identifier):
    print path
    file = open(path, 'rU')
    
    reader = csv.reader(file, delimiter=';', quotechar='"')

    fs = gridfs.GridFS(storage.db, collection='tracefiles')
    
    line = reader.next()
    count = len(line)
    
    file_handles = []
    traces = []
    for i in range(0, count):
        filename = '/' + identifier + '/' + str(i)
        print 'creating: %s' % (filename)
        
        # Create file
        if fs.exists(filename=filename):
            print 'removing existing file %s ' % (filename) 
            to_del = fs.get_last_version(filename=filename)
            fs.delete(to_del._id)
        
        file_handles.append(fs.new_file(filename=filename))
        
        # Create trace
        traces.append(trace_pb2.Trace())
        traces[i].name = filename
    
    for line in reader:
        for i in range(0, count):
            element = traces[i].elements.add()
            element.start = int(0)
            element.stop = int(0)
            element.value = int(line[i])
    
    # Serialize all traces to files
    for i in range(0, count):
        file_handles[i].write(traces[i].SerializeToString())
        create_timeseries(traces[i].name, file_handles[i]._id)
    
        file_handles[i].close()
    
if __name__ == '__main__':

    # Configuration #############
    # List of files with O2 data
    files = [
                          ('D:\work\data\O2 time series\eai-bcs-hour.csv', 'retail'),
                          ('D:\work\data\O2 time series\eai-rcs-hour.csv', 'business'),
                          ]
    # ###########################

    for file in files:
        print file
        load_trace(file[0], 'O2 RAW %s' % (file[1]))

    print 'done'
