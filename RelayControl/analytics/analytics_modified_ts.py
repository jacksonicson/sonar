from service import times_client
from workload import profiles, util as wutil
import numpy as np

##########################
## Configuration        ##
##########################
selected = profiles.mix_2
##########################

connection = times_client.connect()

mean_deltas = []
mean_sds = []
mean_50til = []
mean_90til = []
mean_corr = []

print '%s \t %s \t %s \t %s \t %s' % ('name', 'mean', 'sd', '50th', '90th')
for desc in selected:
    # Load normal CPU trace
    default = desc.name + profiles.POSTFIX_NORM
    ts_default = connection.load(default)
    ar_default = wutil.to_array(ts_default)[1]
    
    # Load modified CPU trace 
    modified = default + profiles.POSTFIX_MODIFIED
    ts_modified = connection.load(modified)
    ar_modified = wutil.to_array(ts_modified)[1]

    # Calculate mean    
    mean_default = np.mean(ar_default)
    mean_modified = np.mean(ar_modified)
    mean_deltas.append(mean_modified - mean_default) 
    
    # Calculate SDs
    stdev_default = np.std(ar_default)
    stdev_modified = np.std(ar_modified)
    mean_sds.append(stdev_modified - stdev_default)
    
    # Calculate percentiles
    p50th_default = np.percentile(ar_default, 50)
    p50th_modified = np.percentile(ar_modified, 50)
    mean_50til.append(p50th_modified - p50th_default)
    
    p90th_default = np.percentile(ar_default, 90)
    p90th_modified = np.percentile(ar_modified, 90)
    mean_90til.append(p90th_modified - p90th_default)

    # Correlation coefficient    
    corr = np.corrcoef(ar_default, ar_modified)[0, 1]
    mean_corr.append(corr)
    
    # Print for normal
    print '%s' % (desc.name) 
    print ' \t %f \t %f \t %f \t %f' % (mean_default, stdev_default, p50th_default, p90th_default)
    # Print for modified
    print ' \t %f \t %f \t %f \t %f' % (mean_modified, stdev_modified, p50th_modified, p90th_modified)


print 'Mean of delta mean loads: \t %f' % (np.mean(mean_deltas))
print 'Mean of delta standard deviations: \t %f' % (np.mean(mean_sds))
print 'Mean of delta 50 percentiles: \t %f' % (np.mean(mean_50til))
print 'Mean of delta 90 percentiles: \t %f' % (np.mean(mean_90til))
print 'Mean corr coefficient: \t %f' % (np.mean(corr))

times_client.close()
