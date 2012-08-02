import storage
 
def transform_start_allocation(target_id, allocation_identifier):
    
    query = {
             '_id' : target_id
             }
    
    target = storage.targets.find_one(query)
    
    print target
    
    if target['status'] == 'successful' and target['results'] is not None:
        allocation = target['results']['allocation']
        
        json_obj = {
                'identifier' : allocation_identifier,
                'servers' : len(target['custom']['servers']),
                'services' : len(target['custom']['traces']),
                'allocation' : allocation,
                } 
        
        storage.allocations.save(json_obj)
        print 'new allocation saved as %s' % (allocation_identifier)


if __name__ == '__main__':
    # todo
    pass
