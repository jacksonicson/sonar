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

# Descriptor of one profile
class Desc:
    def __init__(self, name, sample_frequency, profile_set):
        self.name = name
        self.sample_frequency = sample_frequency
        self.profile_set = profile_set

# Profile set information
class ProfileSet:
    def __init__(self, sid, cap, day=None):
        self.id = sid 
        self.cap = cap
        self.day = day


# Predefined sets
SET_O2_BUSINESS = ProfileSet(0, None)
SET_O2_RETAIL = ProfileSet(1, None)
SET_SIS = ProfileSet(2, 3000)
SET_SIS_D3 = ProfileSet(3, 3000, 3)
SET_SIS_D8 = ProfileSet(3, 3000, 8)
SET_SIS_D9 = ProfileSet(3, 3000, 9)

MIX_SELECTED_CYCLE_TIME = 24 * 60 * 60
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
            
            Desc('SIS_21_cpu', 5 * 60, SET_SIS_D3),
            Desc('SIS_24_cpu', 5 * 60, SET_SIS_D3),
            Desc('SIS_27_cpu', 5 * 60, SET_SIS_D3),
            Desc('SIS_29_cpu', 5 * 60, SET_SIS_D3),
            Desc('SIS_31_cpu', 5 * 60, SET_SIS_D3),
            Desc('SIS_110_cpu', 5 * 60, SET_SIS_D3),
            Desc('SIS_145_cpu', 5 * 60, SET_SIS_D3),
            Desc('SIS_147_cpu', 5 * 60, SET_SIS_D3),
            Desc('SIS_150_cpu', 5 * 60, SET_SIS_D3),
            Desc('SIS_162_cpu', 5 * 60, SET_SIS_D3),
            Desc('SIS_209_cpu', 5 * 60, SET_SIS_D3),
            Desc('SIS_210_cpu', 5 * 60, SET_SIS_D3),
            Desc('SIS_236_cpu', 5 * 60, SET_SIS_D3),
            Desc('SIS_243_cpu', 5 * 60, SET_SIS_D3),
            Desc('SIS_252_cpu', 5 * 60, SET_SIS_D3),
            Desc('SIS_253_cpu', 5 * 60, SET_SIS_D3),
            Desc('SIS_272_cpu', 5 * 60, SET_SIS_D3),
            Desc('SIS_373_cpu', 5 * 60, SET_SIS_D3),
            
            Desc('SIS_29_cpu', 5 * 60, SET_SIS_D8),
            Desc('SIS_31_cpu', 5 * 60, SET_SIS_D8),
            Desc('SIS_123_cpu', 5 * 60, SET_SIS_D8),
            Desc('SIS_124_cpu', 5 * 60, SET_SIS_D8),
            Desc('SIS_125_cpu', 5 * 60, SET_SIS_D8),
            Desc('SIS_145_cpu', 5 * 60, SET_SIS_D8),
            Desc('SIS_147_cpu', 5 * 60, SET_SIS_D8),
            Desc('SIS_148_cpu', 5 * 60, SET_SIS_D8),
            Desc('SIS_149_cpu', 5 * 60, SET_SIS_D8),
            Desc('SIS_192_cpu', 5 * 60, SET_SIS_D8),
            Desc('SIS_199_cpu', 5 * 60, SET_SIS_D8),
            Desc('SIS_211_cpu', 5 * 60, SET_SIS_D8),
            Desc('SIS_283_cpu', 5 * 60, SET_SIS_D8),
            Desc('SIS_337_cpu', 5 * 60, SET_SIS_D8),
            Desc('SIS_344_cpu', 5 * 60, SET_SIS_D8),
            Desc('SIS_345_cpu', 5 * 60, SET_SIS_D8),
            Desc('SIS_350_cpu', 5 * 60, SET_SIS_D8),
            Desc('SIS_352_cpu', 5 * 60, SET_SIS_D8),
            Desc('SIS_354_cpu', 5 * 60, SET_SIS_D8),
            Desc('SIS_357_cpu', 5 * 60, SET_SIS_D8),
            Desc('SIS_383_cpu', 5 * 60, SET_SIS_D8),
            
            Desc('SIS_207_cpu', 5 * 60, SET_SIS_D9),
            Desc('SIS_208_cpu', 5 * 60, SET_SIS_D9),
            Desc('SIS_210_cpu', 5 * 60, SET_SIS_D9),
            Desc('SIS_211_cpu', 5 * 60, SET_SIS_D9),
            Desc('SIS_213_cpu', 5 * 60, SET_SIS_D9),
            Desc('SIS_214_cpu', 5 * 60, SET_SIS_D9),
            Desc('SIS_216_cpu', 5 * 60, SET_SIS_D9),
            Desc('SIS_219_cpu', 5 * 60, SET_SIS_D9),
            Desc('SIS_220_cpu', 5 * 60, SET_SIS_D9),
            Desc('SIS_221_cpu', 5 * 60, SET_SIS_D9),
            Desc('SIS_222_cpu', 5 * 60, SET_SIS_D9),
            Desc('SIS_223_cpu', 5 * 60, SET_SIS_D9),
            Desc('SIS_225_cpu', 5 * 60, SET_SIS_D9),
            Desc('SIS_234_cpu', 5 * 60, SET_SIS_D9),
            Desc('SIS_235_cpu', 5 * 60, SET_SIS_D9),
            Desc('SIS_243_cpu', 5 * 60, SET_SIS_D9),
            Desc('SIS_245_cpu', 5 * 60, SET_SIS_D9),
            Desc('SIS_264_cpu', 5 * 60, SET_SIS_D9),
            Desc('SIS_269_cpu', 5 * 60, SET_SIS_D9),
            Desc('SIS_270_cpu', 5 * 60, SET_SIS_D9),
            Desc('SIS_271_cpu', 5 * 60, SET_SIS_D9),
            Desc('SIS_275_cpu', 5 * 60, SET_SIS_D9),
            Desc('SIS_279_cpu', 5 * 60, SET_SIS_D9),
            Desc('SIS_312_cpu', 5 * 60, SET_SIS_D9),
            Desc('SIS_315_cpu', 5 * 60, SET_SIS_D9),
            Desc('SIS_328_cpu', 5 * 60, SET_SIS_D9),
            Desc('SIS_385_cpu', 5 * 60, SET_SIS_D9),
            Desc('SIS_386_cpu', 5 * 60, SET_SIS_D9),
            Desc('SIS_387_cpu', 5 * 60, SET_SIS_D9),
            ]

mix_0 = [
            Desc('O2_business_ADDORDER', 60 * 60, SET_O2_BUSINESS),
            Desc('O2_business_SENDMSG', 60 * 60, SET_O2_BUSINESS),
            Desc('O2_business_UPDATEACCOUNT', 60 * 60, SET_O2_BUSINESS),
            Desc('O2_retail_ADDORDER', 60 * 60, SET_O2_RETAIL),
            
            Desc('SIS_161_cpu', 5 * 60, SET_SIS),
            Desc('SIS_162_cpu', 5 * 60, SET_SIS),
            Desc('SIS_163_cpu', 5 * 60, SET_SIS),
            Desc('SIS_175_cpu', 5 * 60, SET_SIS),
            Desc('SIS_177_cpu', 5 * 60, SET_SIS),
            Desc('SIS_179_cpu', 5 * 60, SET_SIS),
            Desc('SIS_188_cpu', 5 * 60, SET_SIS),
            Desc('SIS_269_cpu', 5 * 60, SET_SIS),
            Desc('SIS_298_cpu', 5 * 60, SET_SIS),
            Desc('SIS_305_cpu', 5 * 60, SET_SIS),
            Desc('SIS_308_cpu', 5 * 60, SET_SIS),
            Desc('SIS_310_cpu', 5 * 60, SET_SIS),
            Desc('SIS_340_cpu', 5 * 60, SET_SIS),
            Desc('SIS_393_cpu', 5 * 60, SET_SIS),
            Desc('SIS_397_cpu', 5 * 60, SET_SIS),
            
            Desc('SIS_29_cpu', 5 * 60, SET_SIS_D3),
            ]

mix_1 = [
         Desc('SIS_397_cpu', 5 * 60, SET_SIS),
         
         Desc('SIS_199_cpu', 5 * 60, SET_SIS_D8),
         Desc('SIS_207_cpu', 5 * 60, SET_SIS_D9),
         Desc('SIS_211_cpu', 5 * 60, SET_SIS_D9),
         Desc('SIS_213_cpu', 5 * 60, SET_SIS_D9),
         Desc('SIS_216_cpu', 5 * 60, SET_SIS_D9),
         Desc('SIS_221_cpu', 5 * 60, SET_SIS_D9),
         Desc('SIS_222_cpu', 5 * 60, SET_SIS_D9),
         Desc('SIS_225_cpu', 5 * 60, SET_SIS_D9),
         Desc('SIS_234_cpu', 5 * 60, SET_SIS_D9),
         Desc('SIS_245_cpu', 5 * 60, SET_SIS_D9),
         Desc('SIS_264_cpu', 5 * 60, SET_SIS_D9),
         Desc('SIS_271_cpu', 5 * 60, SET_SIS_D9),
         Desc('SIS_275_cpu', 5 * 60, SET_SIS_D9),
         Desc('SIS_279_cpu', 5 * 60, SET_SIS_D9),
         Desc('SIS_344_cpu', 5 * 60, SET_SIS_D8),
         Desc('SIS_345_cpu', 5 * 60, SET_SIS_D8),
         Desc('SIS_350_cpu', 5 * 60, SET_SIS_D8),
         Desc('SIS_385_cpu', 5 * 60, SET_SIS_D9),
         Desc('SIS_387_cpu', 5 * 60, SET_SIS_D9),
         ]

mix_2 = [
         Desc('O2_business_ADDORDER', 60 * 60, SET_O2_BUSINESS),
         Desc('O2_business_SENDMSG', 60 * 60, SET_O2_BUSINESS),
         Desc('O2_business_UPDATEACCOUNT', 60 * 60, SET_O2_BUSINESS),
         
         Desc('SIS_163_cpu', 5 * 60, SET_SIS),
         Desc('SIS_175_cpu', 5 * 60, SET_SIS),
         Desc('SIS_179_cpu', 5 * 60, SET_SIS),
         Desc('SIS_298_cpu', 5 * 60, SET_SIS),
         Desc('SIS_310_cpu', 5 * 60, SET_SIS),
         Desc('SIS_340_cpu', 5 * 60, SET_SIS),
         
         Desc('SIS_29_cpu', 5 * 60, SET_SIS_D3),
         Desc('SIS_199_cpu', 5 * 60, SET_SIS_D8),
         Desc('SIS_211_cpu', 5 * 60, SET_SIS_D9),
         Desc('SIS_216_cpu', 5 * 60, SET_SIS_D9),
         Desc('SIS_225_cpu', 5 * 60, SET_SIS_D9),
         Desc('SIS_234_cpu', 5 * 60, SET_SIS_D9),
         Desc('SIS_264_cpu', 5 * 60, SET_SIS_D9),
         Desc('SIS_279_cpu', 5 * 60, SET_SIS_D9),
         Desc('SIS_345_cpu', 5 * 60, SET_SIS_D8),
         Desc('SIS_387_cpu', 5 * 60, SET_SIS_D9),
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
        profile = convolution.process_trace(connection, desc.name, desc.sample_frequency, MIX_SELECTED_CYCLE_TIME)
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
        # Adapt frequency for the benchmark duration
        profile *= 500
        BENCHMARK_DURATION = 6 * 60 * 60
        frequency = frequency / (MIX_SELECTED_CYCLE_TIME / BENCHMARK_DURATION)
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
        profile = sampleday.process_trace(connection, desc.name, desc.sample_frequency, MIX_SELECTED_CYCLE_TIME, day=desc.profile_set.day, plot=False)
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
        user_profile = np.array(profile)
        frequency = frequency / (MIX_SELECTED_CYCLE_TIME / BENCHMARK_DURATION)
        if save:
            _store_profile(connection, desc.name + '_profile_user', profile, frequency)
        
        # Plotting    
        fig = plt.figure()
        
        ax = fig.add_subplot(111)
        ax.axis([0.0, len(norm_profile), 0, 1])
        ax.plot(range(0, len(norm_profile)), norm_profile)
        
        plt.savefig('C:/temp/convolution/' + desc.name + '_sd.png')
        
    # plt.show()
    times_client.close()
  
  
def _build_all_profiles():
    connection = times_client.connect()
    
    # Because of the 32bit memory limitation not all 
    # TS data can be processes at once. 
    queries = [#('O2_business_[A-Z]+$', 60 * 60, SET_O2_BUSINESS),
               #('O2_retail_[A-Z]+$', 60 * 60, SET_O2_RETAIL),
               ('SIS_1[0-9]*_cpu$', 5 * 60, SET_SIS),
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


def _build(mix, save):
    sample_day = []
    profile = []
    for desc in mix: 
        if desc.profile_set.day != None:
            sample_day.append(desc)
        else:
            profile.append(desc)
            
    print 'Build sample days %i' % (len(sample_day))
    #_build_sample_day(sample_day, save)
    print 'Build profiles %i' % (len(profile))
    _build_profile(profile, save)
    
if __name__ == '__main__':
    _build(mix_selected, save=False)
    # _build_all_profiles()

