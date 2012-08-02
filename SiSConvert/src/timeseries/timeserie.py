from proto import trace_pb2
import configuration.storage as storage
import csv
import gridfs
import os

def create_timeseries(name, file_id, temporary=False, frequency=5.0):
    
    query = {
             'name' : name
             }
    results = storage.timeseries.find(query)
    for result in results: 
        print 'removing timeseries %s' % (result['_id'])
        storage.timeseries.remove(result['_id'])
    
    json_obj = {
                'name' : name,
                
                'file' : file_id,
                'limit' : 200.0,
                'sampling_rate' : float(frequency),
                'shift' : 0.0,
                'temporary' : temporary,
                }
    
    id = storage.timeseries.save(json_obj)
    return id


def write_list(data, filename, frequency):
    """
    frequency: time between two samples in seconds 
    """
    
    print 'creating: %s' % (filename)
        
    fs = gridfs.GridFS(storage.db, collection='tracefiles')
        
    # Create file
    if fs.exists(filename=filename):
        print 'removing existing file %s ' % (filename) 
        to_del = fs.get_last_version(filename=filename)
        fs.delete(to_del._id)
    
    file_handle = fs.new_file(filename=filename)
    
    # Create trace
    trace = trace_pb2.Trace()
    trace.name = filename
    
    # Fill trace with data
    for value in data:
        element = trace.elements.add()
        element.start = int(0)
        element.stop = int(0)
        element.value = value
    
    # Serialize all traces to files
    file_handle.write(trace.SerializeToString())
    create_timeseries(trace.name, file_handle._id, True, frequency)

    file_handle.close()

