from service import times_client
from workload import profiles, util as wutil
import numpy as np

connection = times_client.connect()

print 'Name, Mean delta, Stdev delta, Corrcoef, 50%til'

corr_count = 0
for desc in profiles.mix_0: 
    default = desc.name + profiles.POSTFIX_NORM
    modified = default + profiles.POSTFIX_MODIFIED
    
    ts_default = connection.load(default)
    ts_modified = connection.load(modified)
    
    ar_default = wutil.to_array(ts_default)[1]
    ar_modified = wutil.to_array(ts_modified)[1]
    
    mean_default = np.mean(ar_default)
    mean_modified = np.mean(ar_modified) 
    
    stdev_default = np.std(ar_default)
    stdev_modified = np.std(ar_modified)
    
    p50th_default = np.percentile(ar_default, 0.5)
    p50th_modified = np.percentile(ar_modified, 0.5)
     
    p90th_default = np.percentile(ar_default, 0.9)
    p90th_modified = np.percentile(ar_modified, 0.9)
    
    corr = np.corrcoef(ar_default, ar_modified)[0, 1]
    if corr > 0.5:
        corr_count += 1
    elif corr < -0.5:
        corr_count += 1

    print '%s, %f, %f, %f, %f, %f' % (desc.name, abs(mean_default - mean_modified), abs(stdev_default - stdev_modified),
                                   corr, abs(p50th_default - p50th_modified), abs(p90th_default - p90th_modified))    

print corr_count

times_client.close()
