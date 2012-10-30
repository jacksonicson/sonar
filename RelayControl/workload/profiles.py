'''
List of TS and workload profiles used by the benchmark (stored in Times)
'''

from service import times_client
from times import ttypes
import matplotlib.pyplot as plt
import numpy as np
import util

'''
Times file organization: 
TODO
'''

'''
Prefix and post-fixes used to store data in Times
'''
POSTIFX_ORIG = '' # original RAW time series imported from the SIS or O2 data set. This is NO profile!!!
POSTFIX_RAW = '_profile' # profile generated from the raw data of the SIS or O2 data set 
POSTFIX_NORM = '_profile_norm' # Normalized profile against the set maximum, see mix_selected and ProfileSet class
POSTFIX_USER = '_profile_user' # Normalized profile multiplied with the max. number of users
POSTFIX_DAY = '_sampleday' # A sample day of the time series

POSTFIX_TRACE = '_profile_trace' # Recorded profile which resulted using the user profile in the load driver
POSTFIX_MODIFIED = '_modified' # A modified trace

'''
Experiment specific settings
Everything is in SECONDS
'''
CYCLE_TIME = 24 * 60 * 60 # 24 hours cycle
PROFILE_WIDTH = CYCLE_TIME / (5 * 60) # For each 5 minutes there is one data point in a workload profile
EXPERIMENT_DURATION = 6 * 60 * 60 # 6 hours steady-state duration of the experiment
MAX_USERS = 200 # Maximum number of users
RAMP_UP = 10 * 60 # Ramp up duration of the experiment
RAMP_DOWN = 10 * 60 # Ramp down duration of the experiment

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

# List of profile days
SET_SIS_D3 = ProfileSet(3, 5 * 60, 3000, day=3)
SET_SIS_D8 = ProfileSet(3, 5 * 60, 3000, day=8)
SET_SIS_D9 = ProfileSet(3, 5 * 60, 3000, day=9)

# List of appropriate TS data
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

# MIX0
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

# MIX1
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

# MIX2
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
         Desc('SIS_199_cpu', SET_SIS_D8),
         ]

##############################
## CONFIGURATION            ##
##############################
selected_name = 'mix_2'
selected = mix_2
##############################


def byindex(index):
    return selected[index]


def __write_profile(connection, name, profile_ts, interval):
    '''
    Saves a TS in the Times service.
    
    Keyword arguments:
    connection -- The connection as returned by the Times client
    name -- Name of the TS
    profile_ts -- A numpy array which contains the elements of the TS
    interval -- The time delta between two data points in the profile_ts TS (in seconds) 
    '''
    
    # Check if the profile exists
    if len(connection.find(name)) > 0:
        print 'removing existing data file'
        connection.remove(name)
        
    # Store profile
    print 'storing profile with name %s' % (name)
    connection.create(name, interval)
    
    elements = []
    for i in xrange(len(profile_ts)):
        item = profile_ts[i]
        
        element = ttypes.Element()
        element.timestamp = i * interval
        element.value = item 
        elements.append(element)

    connection.append(name, elements)


def __store_profile(connection, desc, set_max, profile, interval, save=False):
    '''
    Store a profile into Times. Three TS get saved: 
    1) the profile_ts as it is 
    2) a normalized profile profile_norm. set_max is used for normalizing profile_ts
    3) a user profile_user gets generated by multiplying profile_norm with MAX_USERS
     
    The interval of 1) and 2) are as given. The interval of 3) profile_user is updated so that the
    length of the TS multiplied with the interval matches the EXPERIMENT_DURATION. 
    
    connection -- the connection object returned by Times client
    desc -- description object of the TS
    set_max -- maximum value which is used to generate a normalized and user time series
    profile -- TS of the profile
    interval -- duration of one element of the profile TS  
    save -- save the TS into Times (default=False dry run, nothing will be saved)
    '''
    
    # Get the profile set
    pset = desc.profile_set
    
    # Store RAW profiles (-> plotting)
    raw_profile = np.array(profile)
    if save:
        __write_profile(connection, desc.name + POSTFIX_RAW, raw_profile, interval)
    
    # Store NORMALIZED profiles (normalized with the set maximum, see above) (-> feed into SSAPv)
    maxval = float(set_max[pset.id])
    profile /= maxval
    norm_profile = np.array(profile)
    norm_profile *= 100 # Times does not support float values
    if save:
        __write_profile(connection, desc.name + POSTFIX_NORM, norm_profile, interval)
    
    # Store USER profiles (-> feed into Rain)
    # - Adapt interval for the benchmark duration
    # - Add padding for ramp up and ramp down
    profile *= MAX_USERS
    interval = interval / (CYCLE_TIME / EXPERIMENT_DURATION)
    user_profile = np.array(profile)
    user_profile = __padprofile(user_profile, interval)
    if save:
        __write_profile(connection, desc.name + POSTFIX_USER, user_profile, interval)
    
    # Plotting    
    util.plot(user_profile, desc.name + '.png', MAX_USERS)


def __build_sample_day(mix, save):
    connection = times_client.connect()

    # Calculate profiles
    profiles = []
    for desc in mix:
        print 'processing sample day %s' % (desc.name)
        import sampleday
        profile = sampleday.process_trace(connection, desc.name, desc.sample_frequency, CYCLE_TIME, desc.profile_set.day)
        profiles.append(profile)
        
    # Max value in each set of TS
    set_max = __get_set_max(mix, profiles)

    # Store profiles
    for i in xrange(len(mix)):
        desc = mix[i]
        profile, frequency = profiles[i]
        __store_profile(connection, desc, set_max, profile, frequency, save)
        
    times_client.close()
 
 
def __build_modified(save=True):
    
    connection = times_client.connect()
    results = connection.find('.*%s$' % POSTFIX_NORM)
    for result in results:
        ts = connection.load(result)
        print '%s - %i' % (result, ts.frequency)
    times_client.close()
    return
    
    import modifier
    connection = times_client.connect()
    results = connection.find('.*%s$' % POSTFIX_NORM)
    times_client.close()
    for result in results:
        # Validate that a normalized profile is used
        if result.find(POSTFIX_NORM) == -1:
            print 'Skipping %s, no normalized profile' % result
            continue
        
        connection = times_client.connect()
        print 'Processing %s' % result
        modified_profile, frequency = modifier.process_trace(connection, result)
        times_client.close()
        
        connection = times_client.connect()
        if save:
            name = result + POSTFIX_MODIFIED
            print 'Writing profile: %s' % name
            __write_profile(connection, name, modified_profile, frequency)
#            print modified_profile
            
        # Store USER profiles (-> feed into Rain)
        # Adapt frequency for the benchmark duration
        # Add padding for ramp up and ramp down
        modified_profile /= 100.0
        modified_profile *= MAX_USERS
        frequency = frequency / (CYCLE_TIME / EXPERIMENT_DURATION)
        user_profile = np.array(modified_profile)
        # user_profile, frequency = __padprofile((user_profile, frequency))
        if save:
            name = result.replace(POSTFIX_NORM, POSTFIX_USER) + POSTFIX_MODIFIED
            print 'Writing profile: %s' % name 
            __write_profile(connection, name, user_profile, frequency)
#            print user_profile
        times_client.close()


def __build_profiles(mix, save):
    '''
    Build the profiles for all TS in mix. 
    
    Keyword arguments:
    mix -- set of TS to generate a profile
    save -- save profiles to Times 
    '''
    
    # Times connection
    connection = times_client.connect()

    # Calculate profiles
    profiles = []
    for desc in mix:
        print 'processing convolution: %s' % (desc.name)
        import convolution
        profile = convolution.process_trace(connection, desc.name, desc.sample_frequency, CYCLE_TIME)
        profiles.append(profile)
        
    # Get maximum for each set in mix
    set_max = __get_set_max(mix, profiles)

    # Store profiles
    for i in xrange(len(mix)):
        desc = mix[i]
        profile, frequency = profiles[i]
        __store_profile(connection, desc, set_max, profile, frequency, save)
        
    # Close Times connection
    times_client.close()


def __get_set_max(mix, profiles):
    '''
    Goes over all sets. For each set the maximum value over all TS is determined. This
    value is stored in a map with the set-id as key. 
    '''
    
    # Holds set maximums
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


def __padprofile(profile_ts, interval):
    '''
    Each benchmark runs a ramp-up and a ramp-down phase. The profile used by Rain needs
    to be extended so that it contains data to cover the ramp-up and ramp-down phases. 
    '''
    
    # Number of elements for ramp-up 
    elements = RAMP_UP / interval
    print 'padding ramp up: %i' % (elements)
    
    ramup_pad = np.zeros(elements, np.float)
    mean = np.mean(profile_ts)
    ramup_pad[range(elements)] = mean
    
    # Number of elements for ramp-down
    elements = RAMP_DOWN / interval
    print 'padding ramp down: %i' % (elements)
    rampdown_pad = np.zeros(elements, np.float)
    
    # Add padding to the original user profile for Rain
    curve = np.concatenate((ramup_pad, profile_ts, rampdown_pad))
    return curve 

def __build_all_profiles_for_mix(mix, save):
    # TS for sample day and profile processing
    sample_day = []
    profile = []
    for desc in mix: 
        if desc.profile_set.day != None:
            sample_day.append(desc)
        else:
            profile.append(desc)
            
    print 'Build sample days %i' % (len(sample_day))
    __build_sample_day(sample_day, save)
    
    print 'Build profiles %i' % (len(profile))
    __build_profiles(profile, save)
    

def process_sonar_trace(name, trace_ts, timestamps, save=False):
    # Number of readings to aggregate to downsample the
    # trace to width PROFILE_WIDTH
    readings_to_aggregate = len(trace_ts) / PROFILE_WIDTH
    
    # Create a new array to hold the profile
    profile = np.zeros(PROFILE_WIDTH, dtype=float)
    
    # Downsample the trace to the profile array
    for i in xrange(PROFILE_WIDTH):
        start = readings_to_aggregate * i
        end = min(readings_to_aggregate * (i + 1), len(trace_ts))
        
        # ATTENTION: Using mean here
        profile[i] = np.mean(trace_ts[start:end])
        
    # Calculate interval
    interval = EXPERIMENT_DURATION / PROFILE_WIDTH
        
    # Save the profile
    if save:
        connection = times_client.connect()
        __write_profile(connection, name + POSTFIX_TRACE, profile, interval)
        times_client.close()
    
    
def __plot_complete_mix():
    '''
    Plots all TS of a mix in a single images
    '''
    
    # Connect with times
    connection = times_client.connect()
    
    plot_mix = mix_2
    cols = 5
    rows = len(plot_mix) / cols + 1 
    index = 0
    print rows
    
    fig = plt.figure()
    fig.set_figheight(20)
    fig.set_figwidth(40)
    
    for desc in plot_mix:  
        name = desc.name
        timeSeries = connection.load(name + POSTFIX_USER)
        _, demand = util.to_array(timeSeries)
        
        index += 1
        ax = fig.add_subplot(rows, cols, index)
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        ax.plot(range(0, len(demand)), demand)

    plt.savefig('D:/work/dev/sonar/docs/mix2.png')
    
    # Close times connection
    times_client.close()


def dump(logger):
    logger.info('selected_name = %s' % selected_name)
    
    
# Builds the profiles and saves them in Times
if __name__ == '__main__':
    __build_modified()





