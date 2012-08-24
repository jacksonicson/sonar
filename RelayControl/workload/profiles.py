from service import times_client
from times import ttypes
import convolution
import matplotlib.pyplot as plt
import numpy as np

'''
List of workload profiles used by the benchmark (stored in Times)
Times profile names use the prefix "_profile"
(name, frequency, set)
'''

POSTFIX_RAW = '_profile'
POSTFIX_NORM = '_profile_norm'
POSTFIX_USER = '_profile_user'
SETS = ['O2', 'SIS']

selected_profile_cycle = 24 * 60 * 60
selected_profile_width = 120
selected = [('O2_business_UPDATEDSSLINE', 60 * 60, 0), # Burst in the evening
            ('O2_business_ADDUCP', 60 * 60, 0), # Day workload
            ('O2_business_LINECONFIRM', 60 * 60, 0), # Day and night workload
            ('O2_retail_ADDORDER', 60 * 60, 0), # Night and low day workload
            ('O2_retail_SENDMSG', 60 * 60, 0), # Day workload flattens till evening
            ('O2_retail_PORTORDER', 60 * 60, 0), # Random spikes 
            ('O2_retail_UPDATEDSS', 60 * 60, 0), # Night workload
            ('SIS_221_cpu', 5 * 60, 1), # Evening workload 
            ('SIS_194_cpu', 5 * 60, 1), # Average day high evening workload 
            ('SIS_375_cpu', 5 * 60, 1), # Trend to full CPU utilization starting in the morning
            ('SIS_213_cpu', 5 * 60, 1), # High dynamic range 
            ('SIS_211_cpu', 5 * 60, 1), # High dynamic range
            ('SIS_83_cpu', 5 * 60, 1), # Highly volatile varying levels 
            ('SIS_394_cpu', 5 * 60, 1), # Multiple peaks
            ('SIS_381_cpu', 5 * 60, 1), # High volatile 
            ('SIS_383_cpu', 5 * 60, 1), # Bursts and then slow
            ('SIS_415_cpu', 5 * 60, 1), # Volatility bursts  
            ('SIS_198_cpu', 5 * 60, 1), # Random
            ('SIS_269_cpu', 5 * 60, 1), # Random
            ]
    

mix0_profile_cycle = 24 * 60 * 60
mix0_profile_width = 120
mix0 = [('O2_business_UPDATEDSSLINE', 60 * 60, 0), # Burst in the evening
            ('O2_business_ADDUCP', 60 * 60, 0), # Day workload
            ('O2_business_LINECONFIRM', 60 * 60, 0), # Day and night workload
            ('O2_retail_ADDORDER', 60 * 60, 0), # Night and low day workload
            ('O2_retail_SENDMSG', 60 * 60, 0), # Day workload flattens till evening
            ('O2_retail_PORTORDER', 60 * 60, 0), # Random spikes 
            ('O2_retail_UPDATEDSS', 60 * 60, 0), # Night workload
            ('SIS_221_cpu', 5 * 60, 1), # Evening workload 
            ('SIS_194_cpu', 5 * 60, 1), # Average day high evening workload 
            ('SIS_375_cpu', 5 * 60, 1), # Trend to full CPU utilization starting in the morning
            ('SIS_213_cpu', 5 * 60, 1), # High dynamic range 
            ('SIS_211_cpu', 5 * 60, 1), # High dynamic range
            ('SIS_83_cpu', 5 * 60, 1), # Highly volatile varying levels 
            ('SIS_394_cpu', 5 * 60, 1), # Multiple peaks
            ('SIS_381_cpu', 5 * 60, 1), # High volatile 
            ('SIS_383_cpu', 5 * 60, 1), # Bursts and then slow
            ('SIS_415_cpu', 5 * 60, 1), # Volatility bursts  
            ('SIS_198_cpu', 5 * 60, 1), # Random
            ('SIS_269_cpu', 5 * 60, 1), # Random
            ]


def _store_profile(times_connection, name, profile, frequency):
    print 'storing profile with name %s' % (name)
    times_connection.create(name, frequency)
    
    elements = []
    for i in range(0, len(profile)):
        item = profile[i]
        
        element = ttypes.Element()
        element.timestamp = i * 60
        element.value = item 
        elements.append(element)

    times_connection.append(name, elements)

def _build_and_save(mix):
    connection = times_client.connect()

    # Calculate profiles
    profiles = []
    for ts in mix:
        print 'processing %s' % (ts[0])
        profile = convolution.process_trace(connection, ts)
        profiles.append(profile)
        
    # Get maximum for each set
    set_max = {}
    for i in xrange(len(mix)):
        ts = mix[i]
        profilets = profiles[i][0]
        if set_max.has_key(ts[2]) == False:
            set_max[ts[2]] = 0
        tsmax = np.max(profilets)
        set_max[ts[2]] = max(tsmax, set_max[ts[2]])
    
    # Store profiles
    for i in xrange(len(mix)):
        ts = mix[i]
        profile, frequency = profiles[i]
        
        # Store RAW profiles (-> plots)
        raw_profile = np.array(profile)
        _store_profile(connection, ts[0] + '_profile', profile, frequency)
        
        # Store NORMALIZED profiles (normalized with the set maximum, see above) (-> feed into SSAPv)
        maxval = set_max[ts[2]]
        profile /= maxval
        norm_profile = np.array(profile)
        _store_profile(connection, ts[0] + '_profile_norm', profile, frequency)
        
        # Store USER profiles (-> feed into Rain)
        profile *= 500
        frequency = 60 # adjust frequency for time condensed benchmarks 
        user_profile = np.array(profile)
        _store_profile(connection, ts[0] + '_profile_user', profile, frequency)
        
        # Plotting    
        fig = plt.figure()
        
        ax = fig.add_subplot(311)
        ax.plot(range(0, len(raw_profile)), raw_profile)
        
        ax = fig.add_subplot(312)
        ax.plot(range(0, len(norm_profile)), norm_profile)
        
        ax = fig.add_subplot(313)
        ax.plot(range(0, len(user_profile)), user_profile)
        
    # plt.show()
    times_client.close()
    
if __name__ == '__main__':
    # Build profiles and save them
    _build_and_save(mix0)

