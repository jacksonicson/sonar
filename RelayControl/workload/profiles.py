from service import times_client
from times import ttypes
import convolution
import matplotlib.pyplot as plt
import numpy as np
import sampleday

'''
List of workload profiles used by the benchmark (stored in Times)
Times profile names use the prefix "_profile"
(name, frequency, set)
'''

POSTFIX_RAW = '_profile'
POSTFIX_NORM = '_profile_norm'
POSTFIX_USER = '_profile_user'

class ProfileSet:
    def __init__(self, sid, cap):
        self.id = sid 
        self.cap = cap

class Desc:
    def __init__(self, name, sample_frequency, profile_set):
        self.name = name
        self.sample_frequency = sample_frequency
        self.profile_set = profile_set

SET_O2_BUSINESS = ProfileSet(0, None)
SET_O2_RETAIL = ProfileSet(1, None)
SET_SIS = ProfileSet(2, 3000)

mix_selected_cycle_time = 24 * 60 * 60
mix_selected_profile_length = 120
mix_selected = [
            Desc('O2_business_ADDORDER', 60 * 60, SET_O2_BUSINESS),
            Desc('O2_business_ADDLINEORDER', 60 * 60, SET_O2_BUSINESS),
            Desc('O2_business_CONTRACTEXT', 60 * 60, SET_O2_BUSINESS),
            Desc('O2_business_SENDMSG', 60 * 60, SET_O2_BUSINESS),
            Desc('O2_business_UPDATEACCOUNT', 60 * 60, SET_O2_BUSINESS),
            Desc('O2_business_UPDATEDSS', 60 * 60, SET_O2_BUSINESS),
            
            Desc('O2_retail_ADDORDER', 60 * 60, SET_O2_RETAIL),
            Desc('O2_retail_CONTRACTEXT', 60 * 60, SET_O2_RETAIL),
            Desc('O2_retail_ADDUCP', 60 * 60, SET_O2_RETAIL),
            Desc('O2_retail_SENDMSG', 60 * 60, SET_O2_RETAIL),
            Desc('O2_retail_UPDATEACCOUNT', 60 * 60, SET_O2_RETAIL),
            Desc('O2_retail_UPDATEDSS', 60 * 60, SET_O2_RETAIL),
            
            Desc('SIS_161_cpu', 5 * 60, SET_SIS),
            Desc('SIS_162_cpu', 5 * 60, SET_SIS),
            Desc('SIS_163_cpu', 5 * 60, SET_SIS),
            Desc('SIS_172_cpu', 5 * 60, SET_SIS),
            Desc('SIS_175_cpu', 5 * 60, SET_SIS),
            Desc('SIS_177_cpu', 5 * 60, SET_SIS),
            Desc('SIS_178_cpu', 5 * 60, SET_SIS),
            Desc('SIS_179_cpu', 5 * 60, SET_SIS),
            Desc('SIS_188_cpu', 5 * 60, SET_SIS),
            Desc('SIS_189_cpu', 5 * 60, SET_SIS),
            Desc('SIS_198_cpu', 5 * 60, SET_SIS),
            Desc('SIS_194_cpu', 5 * 60, SET_SIS),
            
            
            Desc('SIS_209_cpu', 5 * 60, SET_SIS),
            Desc('SIS_240_cpu', 5 * 60, SET_SIS),
            Desc('SIS_253_cpu', 5 * 60, SET_SIS),
            Desc('SIS_269_cpu', 5 * 60, SET_SIS),
            Desc('SIS_292_cpu', 5 * 60, SET_SIS),
            Desc('SIS_298_cpu', 5 * 60, SET_SIS),
            
            Desc('SIS_305_cpu', 5 * 60, SET_SIS),
            Desc('SIS_308_cpu', 5 * 60, SET_SIS),
            Desc('SIS_309_cpu', 5 * 60, SET_SIS),
            Desc('SIS_310_cpu', 5 * 60, SET_SIS),
            Desc('SIS_313_cpu', 5 * 60, SET_SIS),
            Desc('SIS_314_cpu', 5 * 60, SET_SIS),
            Desc('SIS_340_cpu', 5 * 60, SET_SIS),
            Desc('SIS_374_cpu', 5 * 60, SET_SIS),
            Desc('SIS_393_cpu', 5 * 60, SET_SIS),
            Desc('SIS_394_cpu', 5 * 60, SET_SIS),
            Desc('SIS_397_cpu', 5 * 60, SET_SIS),
            ]


def _store_profile(connection, name, profile_ts, frequency):
    print 'storing profile with name %s' % (name)
    connection.create(name, frequency)
    
    elements = []
    for i in xrange(len(profile_ts)):
        item = profile_ts[i]
        
        element = ttypes.Element()
        element.timestamp = i * frequency
        element.value = item 
        elements.append(element)

    connection.append(name, elements)


def _build_profile(mix, save=False):
    connection = times_client.connect()

    # Calculate profiles
    profiles = []
    for desc in mix:
        print 'processing %s' % (desc.name)
        cdesc = (desc.name, desc.sample_frequency, mix_selected_cycle_time)
        profile = convolution.process_trace(connection, *cdesc)
        profiles.append(profile)
        
    # Get maximum for each set (key is set_id)
    set_max = {}
    for i in xrange(len(mix)):
        desc = mix[i]
        profile_ts = profiles[i][0]
        pset = desc.profile_set
        
        if set_max.has_key(pset.id) == False:
            set_max[pset.id] = 0
            
        max_value = np.max(profile_ts)
        set_max[pset.id] = max(max_value, set_max[pset.id])

    # Store profiles
    for i in xrange(len(mix)):
        desc = mix[i]
        pset = desc.profile_set
        profile, frequency = profiles[i]
        
        # Store RAW profiles (-> plots)
        raw_profile = np.array(profile)
        if save:
            _store_profile(connection, desc.name + '_profile', profile, frequency)
        
        # Store NORMALIZED profiles (normalized with the set maximum, see above) (-> feed into SSAPv)
        maxval = set_max[pset.id]
        profile /= maxval
        norm_profile = np.array(profile)
        if save:
            _store_profile(connection, desc.name + '_profile_norm', profile, frequency)
        
        # Store USER profiles (-> feed into Rain)
        profile *= 500
        frequency = 60 # adjust frequency for time condensed benchmarks 
        user_profile = np.array(profile)
        if save:
            _store_profile(connection, desc.name + '_profile_user', profile, frequency)
        
        # Plotting    
        fig = plt.figure()
        
        ax = fig.add_subplot(111)
        ax.axis([0.0, len(norm_profile), 0, 1])
        ax.plot(range(0, len(norm_profile)), norm_profile)
        
        plt.savefig('C:/temp/convolution/' + desc.name + '.png')
        
    # plt.show()
    times_client.close()


def _build_sample_day(mix, save):
    connection = times_client.connect()

    # Calculate profiles
    profiles = []
    for desc in mix:
        print 'processing %s' % (desc.name)
        cdesc = (desc.name, desc.sample_frequency, mix_selected_cycle_time)
        profile = sampleday.process_trace(connection, *cdesc, plot=False)
        profiles.append(profile)
        
    # Get maximum for each set (key is set_id)
    set_max = {}
    for i in xrange(len(mix)):
        desc = mix[i]
        profile_ts = profiles[i][0]
        pset = desc.profile_set
        
        if set_max.has_key(pset.id) == False:
            set_max[pset.id] = 0
            
        max_value = np.max(profile_ts)
        set_max[pset.id] = max(max_value, set_max[pset.id])
        if pset.cap is not None:
            set_max[pset.id] = min(pset.cap, set_max[pset.id])

    # Store profiles
    for i in xrange(len(mix)):
        desc = mix[i]
        pset = desc.profile_set
        profile, frequency = profiles[i]
        
        # Store RAW profiles (-> plots)
        raw_profile = np.array(profile)
        if save:
            _store_profile(connection, desc.name + '_profile', profile, frequency)
        
        # Store NORMALIZED profiles (normalized with the set maximum, see above) (-> feed into SSAPv)
        maxval = set_max[pset.id]
        profile /= maxval
        norm_profile = np.array(profile)
        if save:
            _store_profile(connection, desc.name + '_profile_norm', profile, frequency)
        
        # Store USER profiles (-> feed into Rain)
        profile *= 500
        frequency = 60 # adjust frequency for time condensed benchmarks 
        user_profile = np.array(profile)
        if save:
            _store_profile(connection, desc.name + '_profile_user', profile, frequency)
        
        # Plotting    
        fig = plt.figure()
        
        ax = fig.add_subplot(111)
        ax.axis([0.0, len(norm_profile), 0, 1])
        ax.plot(range(0, len(norm_profile)), norm_profile)
        
        plt.savefig('C:/temp/convolution/' + desc.name + '.png')
        
    # plt.show()
    times_client.close()
  
  
def _build_all_profiles():
    connection = times_client.connect()
    
    # Because of the 32bit memory limitation not all 
    # TS data can be processes at once. 
    queries = [#('O2_business_[A-Z]+$', 60 * 60, SET_O2_BUSINESS),
               ('O2_retail_[A-Z]+$', 60 * 60, SET_O2_RETAIL),
               #('SIS_1[0-9]*_cpu$', 5 * 60, SET_SIS),
               #('SIS_2[0-9]*_cpu$', 5 * 60, SET_SIS),
               #('SIS_3[0-9]*_cpu$', 5 * 60, SET_SIS)
               ]
    
    mix = []
    for regexp in queries:
        results = connection.find(regexp[0])
        for name in results:
            mix.append(Desc(name, regexp[1], regexp[2]))
            
    times_client.close()
    
    # _build_profile(mix, save=False)
    _build_sample_day(mix, save=False)

    
if __name__ == '__main__':
    #_build(selected, save=True)
    _build_all_profiles()

