import storage

def update_timeseries():
    result = storage.timeseries.find()
    
    shift_index = 0
    
    for timeseries in result: 
        print 'updating %s' % (timeseries)
        timeseries['limit'] = 500.0
        timeseries['sampling_rate'] = 5.0 # Minutes
        timeseries['shift'] = float(shift_index * 5.0) # Minutes
        storage.timeseries.save(timeseries)
        
        shift_index += 1
        shift_index = shift_index % 10


def update_targets(suite, state, current_state='new'):
    query = {
             'suite' : suite,
             }
    
    results = storage.targets.find(query)
    
    for result in results:
        if result.has_key('results') is False:
            result['status'] = 'waiting'
            storage.targets.save(result)
        else:
            result['status'] = 'successful'
            storage.targets.save(result)
        
def delete_waiting():
    query = {
             'status' : 'waiting',
             }
    
    results = storage.targets.find(query)
    for result in results: 
        storage.targets.remove(result['_id'])
    
        
if __name__ == '__main__':
    #update_targets('configuration1312490013', 'waiting', 'waiting')
    delete_waiting()

