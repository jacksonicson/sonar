import storage 

def remove_all_targets():
    storage.targets.remove()
    storage.runs.remove()
    print 'all targets have been removed'


def remove_timeseries():
    storage.tsdata.remove()
    storage.timeseries.remove() 


if __name__ == '__main__':
    #remove_all_targets()
    #remove_timeseries()
    