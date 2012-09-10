from service import times_client
from times import ttypes
import compaction
import convolution
import matplotlib.pyplot as plt
import numpy as np
import sampleday
import util

'''
List of TS and workload profiles used by the benchmark (stored in Times)
'''

'''
Prefix and postfixes used to store data in Times
'''
POSTFIX_RAW = '_profile' # raw profile e.g. from SIS or O2
POSTFIX_NORM = '_profile_norm' # Normalized profile against the set maximum
POSTFIX_USER = '_profile_user' # Normalized profile multiplied with the max. number of users
POSTFIX_TRACE = '_profile_trace' # Recorded profile which resulted using the user profile in the load driver

'''
Experiment specific settings
'''
EXPERIMENT_DURATION = 6 * 60 * 60 # 6 hours
MIX_SELECTED_CYCLE_TIME = 24 * 60 * 60 # 24 hours cycle
PROFILE_WIDTH = MIX_SELECTED_CYCLE_TIME / (5 * 60) # For each 5 minutes there is one data point in the profile
MAX_USERS = 200 # Maximum number of users
RAMP_UP = 10 * 60
RAMP_DOWN = 10 * 60

'''
Describes a single TS which is used to generate a profile
'''
class Desc:
    def __init__(self, name, profile_set):
        self.name = name
        self.sample_frequency = profile_set.ifreq
        self.profile_set = profile_set

'''
A profile set describes shared properties between sets of TS
'''
class ProfileSet:
    def __init__(self, sid, ifreq, cap, day=None):
        self.id = sid 
        self.cap = cap
        self.day = day
        self.ifreq = ifreq


# List of profile sets
SET_O2_BUSINESS = ProfileSet(0, 60 * 60, None)
SET_O2_RETAIL = ProfileSet(1, 60 * 60, None)
SET_SIS = ProfileSet(2, 5 * 60, 3000)
SET_SIS_D3 = ProfileSet(3, 5 * 60, 3000, 3)
SET_SIS_D8 = ProfileSet(3, 5 * 60, 3000, 8)
SET_SIS_D9 = ProfileSet(3, 5 * 60, 3000, 9)

mix_selected = [
            Desc('O2_business_ADDORDER', SET_O2_BUSINESS),
            Desc('O2_business_ADDLINEORDER', SET_O2_BUSINESS),
            Desc('O2_business_CONTRACTEXT', SET_O2_BUSINESS),
            Desc('O2_business_SENDMSG', SET_O2_BUSINESS),
            Desc('O2_business_UPDATEACCOUNT', SET_O2_BUSINESS),
            Desc('O2_business_UPDATEDSS', SET_O2_BUSINESS),
            
            Desc('O2_retail_ADDORDER', SET_O2_RETAIL),
            Desc('O2_retail_CONTRACTEXT', SET_O2_RETAIL),
            Desc('O2_retail_ADDUCP', SET_O2_RETAIL),
            Desc('O2_retail_SENDMSG', SET_O2_RETAIL),
            Desc('O2_retail_UPDATEACCOUNT', SET_O2_RETAIL),
            Desc('O2_retail_UPDATEDSS', SET_O2_RETAIL),
            
            Desc('SIS_161_cpu', SET_SIS),
            Desc('SIS_162_cpu', SET_SIS),
            Desc('SIS_163_cpu', SET_SIS),
            Desc('SIS_172_cpu', SET_SIS),
            Desc('SIS_175_cpu', SET_SIS),
            Desc('SIS_177_cpu', SET_SIS),
            Desc('SIS_178_cpu', SET_SIS),
            Desc('SIS_179_cpu', SET_SIS),
            Desc('SIS_188_cpu', SET_SIS),
            Desc('SIS_189_cpu', SET_SIS),
            Desc('SIS_198_cpu', SET_SIS),
            Desc('SIS_194_cpu', SET_SIS),
            Desc('SIS_209_cpu', SET_SIS),
            Desc('SIS_240_cpu', SET_SIS),
            Desc('SIS_253_cpu', SET_SIS),
            Desc('SIS_269_cpu', SET_SIS),
            Desc('SIS_292_cpu', SET_SIS),
            Desc('SIS_298_cpu', SET_SIS),
            Desc('SIS_305_cpu', SET_SIS),
            Desc('SIS_308_cpu', SET_SIS),
            Desc('SIS_309_cpu', SET_SIS),
            Desc('SIS_310_cpu', SET_SIS),
            Desc('SIS_313_cpu', SET_SIS),
            Desc('SIS_314_cpu', SET_SIS),
            Desc('SIS_340_cpu', SET_SIS),
            Desc('SIS_374_cpu', SET_SIS),
            Desc('SIS_393_cpu', SET_SIS),
            Desc('SIS_394_cpu', SET_SIS),
            Desc('SIS_397_cpu', SET_SIS),
            
            Desc('SIS_21_cpu', SET_SIS_D3),
            Desc('SIS_24_cpu', SET_SIS_D3),
            Desc('SIS_27_cpu', SET_SIS_D3),
            Desc('SIS_29_cpu', SET_SIS_D3),
            Desc('SIS_31_cpu', SET_SIS_D3),
            Desc('SIS_110_cpu', SET_SIS_D3),
            Desc('SIS_145_cpu', SET_SIS_D3),
            Desc('SIS_147_cpu', SET_SIS_D3),
            Desc('SIS_150_cpu', SET_SIS_D3),
            Desc('SIS_162_cpu', SET_SIS_D3),
            Desc('SIS_209_cpu', SET_SIS_D3),
            Desc('SIS_210_cpu', SET_SIS_D3),
            Desc('SIS_236_cpu', SET_SIS_D3),
            Desc('SIS_243_cpu', SET_SIS_D3),
            Desc('SIS_252_cpu', SET_SIS_D3),
            Desc('SIS_253_cpu', SET_SIS_D3),
            Desc('SIS_272_cpu', SET_SIS_D3),
            Desc('SIS_373_cpu', SET_SIS_D3),
            
            Desc('SIS_29_cpu', SET_SIS_D8),
            Desc('SIS_31_cpu', SET_SIS_D8),
            Desc('SIS_123_cpu', SET_SIS_D8),
            Desc('SIS_124_cpu', SET_SIS_D8),
            Desc('SIS_125_cpu', SET_SIS_D8),
            Desc('SIS_145_cpu', SET_SIS_D8),
            Desc('SIS_147_cpu', SET_SIS_D8),
            Desc('SIS_148_cpu', SET_SIS_D8),
            Desc('SIS_149_cpu', SET_SIS_D8),
            Desc('SIS_192_cpu', SET_SIS_D8),
            Desc('SIS_199_cpu', SET_SIS_D8),
            Desc('SIS_211_cpu', SET_SIS_D8),
            Desc('SIS_283_cpu', SET_SIS_D8),
            Desc('SIS_337_cpu', SET_SIS_D8),
            Desc('SIS_344_cpu', SET_SIS_D8),
            Desc('SIS_345_cpu', SET_SIS_D8),
            Desc('SIS_350_cpu', SET_SIS_D8),
            Desc('SIS_352_cpu', SET_SIS_D8),
            Desc('SIS_354_cpu', SET_SIS_D8),
            Desc('SIS_357_cpu', SET_SIS_D8),
            Desc('SIS_383_cpu', SET_SIS_D8),
            
            Desc('SIS_207_cpu', SET_SIS_D9),
            Desc('SIS_208_cpu', SET_SIS_D9),
            Desc('SIS_210_cpu', SET_SIS_D9),
            Desc('SIS_211_cpu', SET_SIS_D9),
            Desc('SIS_213_cpu', SET_SIS_D9),
            Desc('SIS_214_cpu', SET_SIS_D9),
            Desc('SIS_216_cpu', SET_SIS_D9),
            Desc('SIS_219_cpu', SET_SIS_D9),
            Desc('SIS_220_cpu', SET_SIS_D9),
            Desc('SIS_221_cpu', SET_SIS_D9),
            Desc('SIS_222_cpu', SET_SIS_D9),
            Desc('SIS_223_cpu', SET_SIS_D9),
            Desc('SIS_225_cpu', SET_SIS_D9),
            Desc('SIS_234_cpu', SET_SIS_D9),
            Desc('SIS_235_cpu', SET_SIS_D9),
            Desc('SIS_243_cpu', SET_SIS_D9),
            Desc('SIS_245_cpu', SET_SIS_D9),
            Desc('SIS_264_cpu', SET_SIS_D9),
            Desc('SIS_269_cpu', SET_SIS_D9),
            Desc('SIS_270_cpu', SET_SIS_D9),
            Desc('SIS_271_cpu', SET_SIS_D9),
            Desc('SIS_275_cpu', SET_SIS_D9),
            Desc('SIS_279_cpu', SET_SIS_D9),
            Desc('SIS_312_cpu', SET_SIS_D9),
            Desc('SIS_315_cpu', SET_SIS_D9),
            Desc('SIS_328_cpu', SET_SIS_D9),
            Desc('SIS_385_cpu', SET_SIS_D9),
            Desc('SIS_386_cpu', SET_SIS_D9),
            Desc('SIS_387_cpu', SET_SIS_D9),
            ]

mix_0 = [
            Desc('O2_business_ADDORDER', SET_O2_BUSINESS),
            Desc('O2_business_SENDMSG', SET_O2_BUSINESS),
            Desc('O2_business_UPDATEACCOUNT', SET_O2_BUSINESS),
            Desc('O2_retail_ADDORDER', SET_O2_RETAIL),
            
            Desc('SIS_161_cpu', SET_SIS),
            Desc('SIS_162_cpu', SET_SIS),
            Desc('SIS_163_cpu', SET_SIS),
            Desc('SIS_175_cpu', SET_SIS),
            Desc('SIS_177_cpu', SET_SIS),
            Desc('SIS_179_cpu', SET_SIS),
            Desc('SIS_188_cpu', SET_SIS),
            Desc('SIS_269_cpu', SET_SIS),
            Desc('SIS_298_cpu', SET_SIS),
            Desc('SIS_305_cpu', SET_SIS),
            Desc('SIS_308_cpu', SET_SIS),
            Desc('SIS_310_cpu', SET_SIS),
            Desc('SIS_340_cpu', SET_SIS),
            Desc('SIS_393_cpu', SET_SIS),
            Desc('SIS_397_cpu', SET_SIS),
            
            Desc('SIS_29_cpu', SET_SIS_D3),
            ]

mix_1 = [
         Desc('SIS_397_cpu', SET_SIS),
         Desc('SIS_199_cpu', SET_SIS_D8),
         Desc('SIS_207_cpu', SET_SIS_D9),
         Desc('SIS_211_cpu', SET_SIS_D9),
         Desc('SIS_213_cpu', SET_SIS_D9),
         Desc('SIS_216_cpu', SET_SIS_D9),
         Desc('SIS_221_cpu', SET_SIS_D9),
         Desc('SIS_222_cpu', SET_SIS_D9),
         Desc('SIS_225_cpu', SET_SIS_D9),
         Desc('SIS_234_cpu', SET_SIS_D9),
         Desc('SIS_245_cpu', SET_SIS_D9),
         Desc('SIS_264_cpu', SET_SIS_D9),
         Desc('SIS_271_cpu', SET_SIS_D9),
         Desc('SIS_275_cpu', SET_SIS_D9),
         Desc('SIS_279_cpu', SET_SIS_D9),
         Desc('SIS_344_cpu', SET_SIS_D8),
         Desc('SIS_345_cpu', SET_SIS_D8),
         Desc('SIS_350_cpu', SET_SIS_D8),
         Desc('SIS_385_cpu', SET_SIS_D9),
         Desc('SIS_387_cpu', SET_SIS_D9),
         ]

mix_2 = [
         Desc('O2_business_ADDORDER', SET_O2_BUSINESS),
         Desc('O2_business_SENDMSG', SET_O2_BUSINESS),
         Desc('O2_business_UPDATEACCOUNT', SET_O2_BUSINESS),
         
         Desc('SIS_163_cpu', SET_SIS),
         Desc('SIS_175_cpu', SET_SIS),
         Desc('SIS_179_cpu', SET_SIS),
         Desc('SIS_298_cpu', SET_SIS),
         Desc('SIS_310_cpu', SET_SIS),
         Desc('SIS_340_cpu', SET_SIS),
         
         Desc('SIS_29_cpu', SET_SIS_D3),
         Desc('SIS_199_cpu', SET_SIS_D8),
         Desc('SIS_211_cpu', SET_SIS_D9),
         Desc('SIS_216_cpu', SET_SIS_D9),
         Desc('SIS_225_cpu', SET_SIS_D9),
         Desc('SIS_234_cpu', SET_SIS_D9),
         Desc('SIS_264_cpu', SET_SIS_D9),
         Desc('SIS_279_cpu', SET_SIS_D9),
         Desc('SIS_345_cpu', SET_SIS_D8),
         Desc('SIS_387_cpu', SET_SIS_D9),
         ]

##############################
## CONFIGURATION            ##
selected = mix_2
##############################


def byindex(index):
    return selected[index]


def __write_profile(connection, name, profile_ts, frequency):
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

def __plot(profile, filename, max=1):
    fig = plt.figure()
    
    ax = fig.add_subplot(111)
    ax.axis([0.0, len(profile), 0, max])
    ax.plot(range(0, len(profile)), profile)
    
    try:
        plt.savefig('C:/temp/convolution/' + filename)
    except:
        pass 

def __store_profile(connection, desc, set_max, profile, frequency, save=False):
    pset = desc.profile_set
    
    # Store RAW profiles (-> plots)
    raw_profile = np.array(profile)
    if save:
        __write_profile(connection, desc.name + POSTFIX_RAW, profile, frequency)
    
    # Store NORMALIZED profiles (normalized with the set maximum, see above) (-> feed into SSAPv)
    maxval = float(set_max[pset.id])
    profile /= maxval
    norm_profile = np.array(profile)
    norm_profile *= 100 # Times does not support float values
    if save:
        __write_profile(connection, desc.name + POSTFIX_NORM, norm_profile, frequency)
    
    
    # Store USER profiles (-> feed into Rain)
    # Adapt frequency for the benchmark duration
    # Add padding for ramp up and ramp down
    profile *= MAX_USERS
    frequency = frequency / (MIX_SELECTED_CYCLE_TIME / EXPERIMENT_DURATION)
    user_profile = np.array(profile)
    user_profile, frequency = _padprofile((user_profile, frequency))
    if save:
        __write_profile(connection, desc.name + POSTFIX_USER, user_profile, frequency)
    
    # Plotting    
    __plot(user_profile, desc.name + '.png', MAX_USERS)


def _build_profile(mix, save):
    connection = times_client.connect()

    # Calculate profiles
    profiles = []
    for desc in mix:
        print 'processing %s' % (desc.name)
        profile = convolution.process_trace(connection, desc.name, desc.sample_frequency, MIX_SELECTED_CYCLE_TIME)
        profiles.append(profile)
        
    # Get maximum for each set of ts
    set_max = _get_set_max(mix, profiles)

    # Store profiles
    for i in xrange(len(mix)):
        desc = mix[i]
        profile, frequency = profiles[i]
        __store_profile(connection, desc, set_max, profile, frequency, save)
        
    times_client.close()


def _get_set_max(mix, profiles):
    set_max = {}
    # Get maximum for each set (key is set_id)
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
            
    return set_max

def _padprofile(profile):
    elements = RAMP_UP / profile[1]
    print 'padding ramp up: %i' % (elements)
    
    ramup_pad = np.zeros(elements, np.float)
    mean = np.mean(profile[0])
    ramup_pad[range(elements)] = mean
    
    elements = RAMP_DOWN / profile[1]
    print 'padding ramp down: %i' % (elements)
    rampdown_pad = np.zeros(elements, np.float)
    
    curve = np.concatenate((ramup_pad, profile[0], rampdown_pad))
    profile = (curve, profile[1])
    
    # print profile
    return profile 

def _build_sample_day(mix, save):
    connection = times_client.connect()

    # Calculate profiles
    profiles = []
    for desc in mix:
        print 'processing %s' % (desc.name)
        profile = sampleday.process_trace(connection, desc.name, desc.sample_frequency, MIX_SELECTED_CYCLE_TIME, desc.profile_set.day)
        profiles.append(profile)
        
    # Max value in each set of TS
    set_max = _get_set_max(mix, profiles)

    # Store profiles
    for i in xrange(len(mix)):
        desc = mix[i]
        profile, frequency = profiles[i]
        __store_profile(connection, desc, set_max, profile, frequency, save)
        
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
    
    # Build convolution and sampleday profiles
    _build_profile(mix, save=False)
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
    _build_sample_day(sample_day, save)
    print 'Build profiles %i' % (len(profile))
    _build_profile(profile, save)
    

def process(name, trace, timestamps, save=False):
    agg_count = len(trace) / PROFILE_WIDTH
    profile = np.zeros(PROFILE_WIDTH, dtype=float)
    for i in xrange(PROFILE_WIDTH):
        start = agg_count * i
        end = min(agg_count * (i + 1), len(trace))
        profile[i] = np.mean(trace[start:end])
        
    # Calculate Frequency
    frequency = EXPERIMENT_DURATION / PROFILE_WIDTH
        
    # Connect with times
    connection = times_client.connect()
        
    # Store NORMALIZED profiles (normalized with the set maximum, see above) (-> feed into SSAPv)
    if save:
        __write_profile(connection, name + POSTFIX_TRACE, profile, frequency)
        
    # Close times connection
    times_client.close()
    
    
def _plot():
    # Connect with times
    connection = times_client.connect()
    
#    for desc in selected:  
# des.name
    name = 'SIS_264_cpu'  
    timeSeries = connection.load(name + POSTFIX_TRACE)
    time, demand = util.to_array(timeSeries)
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(range(0, len(demand)), demand)

    plt.show()
    
    # Close times connection
    times_client.close()
    
# Builds the profiles and saves them in Times
if __name__ == '__main__':
    # _build(selected, save=True)
    # _build_all_profiles()
    _plot()





