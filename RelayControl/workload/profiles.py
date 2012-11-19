'''
List of TS and workload profiles used by the benchmark (stored in Times)
'''

from service import times_client
from times import ttypes
from timeutil import * #@UnusedWildImport
import configuration
import matplotlib.pyplot as plt
import modifier
import numpy as np
import plot
import util

'''
Times file organization:
There are still files with names that do not match the syntax below. These files are
not used by any system and are marked as deprecated!
 
[SIS_$NUMBER_mem] - SIS TS for memory
[SIS_$NUMBER_CPU] - SIS TS for CPU

[O2_business_$TYPE] - O2 Business TS with given type
[O2_retail_$TYPE] - O2 Retail TS with given type

[TS] = SIS or O2 TS name
[PX][TS]_profile
[PX][TS]_profile_norm
[PX][TS]_profile_user
[PX][TS]_sampleday

[PX][TS]_profile_trace
[PX][TS][_profile_norm]_modified
[PX][TS][_profile_user]_modified

The interval of _profile_user is updated so that the length of the TS multiplied 
with the interval matches the EXPERIMENT_DURATION.

PX is a prefix which depends on the selected workload mix. 
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
CYCLE_TIME = hour(24) # 24 hours cycle
PROFILE_INTERVAL_COUNT = CYCLE_TIME / minu(5) # For each 5 minutes there is one data point in a workload profile

EXPERIMENT_DURATION = hour(6) # 6 hours steady-state duration of the experiment
RAMP_UP = minu(10) # Ramp up duration of the experiment
RAMP_DOWN = minu(10) # Ramp down duration of the experiment

MAX_USERS = user(200) # Maximum number of users

'''
Generate TS compatible to paper version. COMPATIBLE_AFTER function can be used
to mark code segments to be compatible starting with a version. 
Example.

if COMPATIBLE_AFTER(C): - code is compatible with versions after C (exclusive)
if INCOMPATIBLE_AFTER(C): - code is not compatible with versions after C (still compatible with C)
'''
PAPER_DSS = 0
PAPER_DSS2 = 1 
COMPATIBILITY_MODE = PAPER_DSS2
COMPATIBLE_AFTER = lambda C: COMPATIBILITY_MODE > C
INCOMPATIBLE_AFTER = lambda C: COMPATIBILITY_MODE <= C


class Desc:
    '''
    Describes a single TS which is used to generate a profile
    '''
    def __init__(self, name, profile_set, modifier=None, scale=(0, 0), shift=0, additive=0):
        self.name = name
        self.sample_frequency = profile_set.ifreq
        self.profile_set = profile_set
        
        self.modifier = modifier
        self.scale = scale 
        self.shift = shift
        self.additive = additive

class ProfileSet:
    '''
    A profile set describes shared properties between sets of TS
    '''
    def __init__(self, sid, ifreq, cap, day=None):
        self.id = sid 
        self.cap = cap
        self.day = day
        self.ifreq = ifreq


# List of profile sets
SET_O2_BUSINESS = ProfileSet(0, hour(1), None)
SET_O2_RETAIL = ProfileSet(1, hour(1), None)
SET_SIS = ProfileSet(2, minu(5), 3000)

# List of profile days
SET_SIS_D3 = ProfileSet(3, minu(5), 3000, day=3)
SET_SIS_D8 = ProfileSet(3, minu(5), 3000, day=8)
SET_SIS_D9 = ProfileSet(3, minu(5), 3000, day=9)

# MIX0
mix_0 = [
            Desc('O2_business_ADDORDER', SET_O2_BUSINESS, modifier.MOD8, (1.2, 1), minu(10), 20),
            Desc('O2_business_SENDMSG', SET_O2_BUSINESS, modifier.MOD2, (1.1, 1), minu(-15), 20),
            Desc('O2_business_UPDATEACCOUNT', SET_O2_BUSINESS, modifier.MOD3, (1.3, 1.1), minu(10), 20),
            Desc('O2_retail_ADDORDER', SET_O2_RETAIL, modifier.MOD8, (1, 0.8), minu(30), 10),
            Desc('SIS_161_cpu', SET_SIS, modifier.MOD5, (1.1, 0.9), minu(10), 5),
            Desc('SIS_162_cpu', SET_SIS, modifier.MOD7, (1, 1), minu(15), 20),
            Desc('SIS_163_cpu', SET_SIS, modifier.MOD1, (1, 1.3), minu(0), 20),
            Desc('SIS_175_cpu', SET_SIS, modifier.MOD2, (1.1, 1), minu(-5), 20),
            Desc('SIS_177_cpu', SET_SIS, modifier.MOD8, (1, 1), minu(20), 20),
            Desc('SIS_179_cpu', SET_SIS, modifier.MOD4, (1, 1), minu(-7), 20),
            Desc('SIS_188_cpu', SET_SIS, modifier.MOD5, (1, 1), minu(0), 20),
            Desc('SIS_269_cpu', SET_SIS, modifier.MOD6, (1, 1.1), minu(1), 20),
            Desc('SIS_298_cpu', SET_SIS, modifier.MOD7, (1.1, 1), minu(0), 20),
            Desc('SIS_305_cpu', SET_SIS, modifier.MOD1, (1, 1), minu(-6), 20),
            Desc('SIS_308_cpu', SET_SIS, modifier.MOD7, (1, 1), minu(5), 20),
            Desc('SIS_310_cpu', SET_SIS, modifier.MOD3, (1, 0.9), minu(10), 20),
            Desc('SIS_340_cpu', SET_SIS, modifier.MOD4, (1, 1), minu(15), 20),
            Desc('SIS_393_cpu', SET_SIS, modifier.MOD3, (1.1, 1), minu(0), 20),
            Desc('SIS_397_cpu', SET_SIS, modifier.MOD7, (1.05, 1.1), minu(-10), 20),
            Desc('SIS_29_cpu', SET_SIS_D3, modifier.MOD8, (1, 1), minu(20), 30),
            ]

# MIX1
mix_1 = [
         Desc('SIS_397_cpu', SET_SIS, modifier.MOD7, (1.1, 1), minu(10), 30),
         Desc('SIS_199_cpu', SET_SIS_D8, modifier.MOD7, (1.1, 0.9), minu(-5), 50),
         Desc('SIS_207_cpu', SET_SIS_D9, modifier.MOD4, (1.1, 1), minu(-30), 50),
         Desc('SIS_211_cpu', SET_SIS_D9, modifier.MOD0, (1.2, 0.8), minu(10), 50),
         Desc('SIS_213_cpu', SET_SIS_D9, modifier.MOD5, (1, 1.1), minu(20), 30),
         Desc('SIS_216_cpu', SET_SIS_D9, modifier.MOD5, (1.2, 1), minu(0), 20),
         Desc('SIS_221_cpu', SET_SIS_D9, modifier.MOD7, (1, 1.3), minu(-10), 30),
         Desc('SIS_222_cpu', SET_SIS_D9, modifier.MOD1, (1.0, 1), minu(-50), 30),
         Desc('SIS_225_cpu', SET_SIS_D9, modifier.MOD9, (1.1, 1.3), minu(10), 10),
         Desc('SIS_234_cpu', SET_SIS_D9, modifier.MOD8, (1, 1), minu(50), 40),
         Desc('SIS_245_cpu', SET_SIS_D9, modifier.MOD4, (1.1, 1), minu(0), 20),
         Desc('SIS_264_cpu', SET_SIS_D9, modifier.MOD3, (1, 1), minu(-20), 50),
         Desc('SIS_271_cpu', SET_SIS_D9, modifier.MOD6, (1.1, 1.4), minu(50), 40),
         Desc('SIS_275_cpu', SET_SIS_D9, modifier.MOD5, (1.02, 1.3), minu(15), 10),
         Desc('SIS_279_cpu', SET_SIS_D9, modifier.MOD1, (1.2, 1), minu(30), 10),
         Desc('SIS_344_cpu', SET_SIS_D8, modifier.MOD2, (1.05, 1), minu(6), 30),
         Desc('SIS_345_cpu', SET_SIS_D8, modifier.MOD0, (1.3, 1.1), minu(-100), 30),
         Desc('SIS_350_cpu', SET_SIS_D8, modifier.MOD8, (1, 1), minu(0), 10),
         Desc('SIS_385_cpu', SET_SIS_D9, modifier.MOD3, (1.03, 1.4), minu(10), 20),
         Desc('SIS_387_cpu', SET_SIS_D9, modifier.MOD6, (1.1, 1.7), minu(50), 50),
         ]

# MIX2
mix_2 = [
         Desc('O2_business_ADDORDER', SET_O2_BUSINESS, modifier.MOD1, (1, 1), minu(10), 20),
         Desc('O2_business_SENDMSG', SET_O2_BUSINESS, modifier.MOD7, (1, 1), minu(-5), 20),
         Desc('O2_business_UPDATEACCOUNT', SET_O2_BUSINESS, modifier.MOD8, (1.1, 1), minu(20), 20),
         Desc('SIS_163_cpu', SET_SIS, modifier.MOD4, (1, 1), minu(10), 20),
         Desc('SIS_175_cpu', SET_SIS, modifier.MOD5, (1, 1.1), minu(-20), 20),
         Desc('SIS_179_cpu', SET_SIS, modifier.MOD6, (1, 1), minu(-10), 20),
         Desc('SIS_298_cpu', SET_SIS, modifier.MOD7, (1, 1), minu(0), 20),
         Desc('SIS_310_cpu', SET_SIS, modifier.MOD8, (1.2, 1), minu(0), 10),
         Desc('SIS_340_cpu', SET_SIS, modifier.MOD2, (1, 1), minu(5), 10),
         Desc('SIS_29_cpu', SET_SIS_D3, modifier.MOD3, (1, 1.2), hour(1), 20),
         Desc('SIS_199_cpu', SET_SIS_D8, modifier.MOD4, (1, 1), minu(10), 20),
         Desc('SIS_211_cpu', SET_SIS_D9, modifier.MOD4, (1.03, 1.1), minu(0), 20),
         Desc('SIS_216_cpu', SET_SIS_D9, modifier.MOD7, (1.1, 1), minu(20), 0),
         Desc('SIS_225_cpu', SET_SIS_D9, modifier.MOD7, (1.3, 1), minu(-15), 20),
         Desc('SIS_234_cpu', SET_SIS_D9, modifier.MOD1, (1.4, 1.2), minu(0), 20),
         Desc('SIS_264_cpu', SET_SIS_D9, modifier.MOD2, (1, 1), minu(10), 10),
         Desc('SIS_279_cpu', SET_SIS_D9, modifier.MOD0, (1.2, 1), minu(20), 40),
         Desc('SIS_345_cpu', SET_SIS_D8, modifier.MOD8, (1, 1.5), minu(0), 40),
         Desc('SIS_387_cpu', SET_SIS_D9, modifier.MOD4, (1.3, 1), minu(15), 20),
         Desc('SIS_199_cpu', SET_SIS_D8, modifier.MOD7, (1.1, 1), minu(0), 20),
         ]

##############################
## CONFIGURATION            ##
##############################
selected_profile = None # Prefix for picking TS from Times
selected_name = 'mix_1' # Just for logging
selected = mix_1        # Selected workload mix
modified = True         # Modified version of the workload mix
##############################

def get_current_cpu_profile(index):
    '''
    Gets cpu profile by index from the selected workload mix. The selection
    depends on the modified flag. 
    '''
    if selected_profile is None:
        selected_profile = ''
    else:
        selected_profile += '_'
    
    desc = by_index(index)
    name = selected_profile + desc.name + POSTFIX_NORM
    if modified:
        name += POSTFIX_MODIFIED
        
    print 'Selected cpu profile: %s' % name
    return name


def get_current_user_profile(index):
    '''
    Gets user profile by index from the selected workload mix. The selection
    depends on the modified flag. 
    '''
    if selected_profile is None:
        selected_profile = ''
    else:
        selected_profile += '_'
    
    desc = by_index(index)
    name = selected_profile + desc.name + POSTFIX_USER
    if modified:
        name += POSTFIX_MODIFIED
        
    print 'Selected user profile: %s' % name
    return name 
         

def by_index(index):
    '''
    Get TS description by index
    '''
    return selected[index]


def __write_profile(connection, name, profile_ts, interval, overwrite=False):
    '''
    Saves a TS in the Times service.
    
    Keyword arguments:
    connection -- The connection as returned by the Times client
    name -- Name of the TS
    profile_ts -- A numpy array which contains the elements of the TS
    interval -- The time delta between two data points in the profile_ts TS (in seconds) 
    '''
    
    # Extend name with the current workload mix prefix
    if selected_profile is not None:
        name = selected_profile + '_' + name
    
    # Check if the profile exists
    if len(connection.find(name)) > 0:
        if overwrite:
            print 'removing existing data file'
            connection.remove(name)
        else:
            print 'return - will not overwrite profile %s' % name
            return
        
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
    
    if np.max(user_profile) > MAX_USERS:
        print '%s > max users - %i' % (desc.name + POSTFIX_USER, np.max(user_profile))
        
    if save:
        __write_profile(connection, desc.name + POSTFIX_USER, user_profile, interval)
    
    # Plotting    
    util.plot(user_profile, desc.name + '.png', MAX_USERS)


def __build_sample_day(mix, save):
    connection = times_client.connect()

    # Calculate profiles
    for desc in mix:
        print 'processing sample day %s' % (desc.name)
        import sampleday
        profile = sampleday.process_trace(connection, desc.name, desc.sample_frequency, CYCLE_TIME, desc.profile_set.day)
        desc.profile = profile
        
    # Max value in each set of TS
    set_max = __get_and_apply_set_max(mix)

    # Store profiles
    for desc in mix:
        profile, frequency = desc.profile
        __store_profile(connection, desc, set_max, profile, frequency, save)
        
    times_client.close()
 
 
def build_modified_profiles(mix, save):
    connection = times_client.connect()
    
    for mi_element in mix:
        ts_name = mi_element.name + POSTFIX_NORM

        fig, ax = util.new_plot(util.to_array(connection.load(ts_name))[1], 100)
        
        # Modify normal profile        
        modified_profile, interval = modifier.process_trace(connection, ts_name,
                                                            mi_element.modifier, mi_element.additive,
                                                            mi_element.scale, mi_element.shift)
        
        util.add_plot(fig, ax, modified_profile)
        util.write_plot('%s_ORIGINAL' % ts_name)
        
        if save:
            name = ts_name + POSTFIX_MODIFIED
            print 'Writing profile: %s' % name
            __write_profile(connection, name, modified_profile, interval)
            
        # Store USER profiles (-> feed into Rain)
        # Adapt frequency for the benchmark duration
        # Add padding for ramp up and ramp down
        modified_profile /= 100.0
        modified_profile *= MAX_USERS
        interval = interval / (CYCLE_TIME / EXPERIMENT_DURATION)
        user_profile = np.array(modified_profile)
        user_profile = __padprofile(user_profile, interval)
        if save:
            name = ts_name.replace(POSTFIX_NORM, POSTFIX_USER) + POSTFIX_MODIFIED
            print 'Writing profile: %s' % name 
            __write_profile(connection, name, user_profile, interval)
            

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
    for desc in mix:
        print 'processing convolution: %s' % (desc.name)
        import convolution
        profile = convolution.process_trace(connection, desc.name, desc.sample_frequency, CYCLE_TIME)
        
        # Add profile to mix
        desc.profile = profile
        
    # Get maximum for each set in mix
    set_max = __get_and_apply_set_max(mix)

    # Store profiles
    for desc in mix:
        profile, frequency = desc.profile
        __store_profile(connection, desc, set_max, profile, frequency, save)
        
    # Close Times connection
    times_client.close()


def __get_and_apply_set_max(mix):
    '''
    Goes over all sets. For each set the maximum value over all TS is determined. This
    value is stored in a map with the set-id as key. 
    '''
    
    # Holds set maximums
    set_max = {}
    
    # Get maximum for each set (key is set_id)
    for i in xrange(len(mix)):
        desc = mix[i]
        profile_ts = desc.profile[0]
        
        pset = desc.profile_set
        
        if COMPATIBLE_AFTER(PAPER_DSS): 
            indices = profile_ts > pset.cap
            profile_ts[indices] = pset.cap
        
        if set_max.has_key(pset.id) == False:
            set_max[pset.id] = 0
            
        max_value = np.max(profile_ts)
        set_max[pset.id] = max(max_value, set_max[pset.id])
        
        if INCOMPATIBLE_AFTER(PAPER_DSS) and pset.cap is not None:
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

def build_all_profiles_for_mix(mix, save):
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
    # trace to width PROFILE_INTERVAL_COUNT
    readings_to_aggregate = len(trace_ts) / PROFILE_INTERVAL_COUNT
    
    # Create a new array to hold the profile
    profile = np.zeros(PROFILE_INTERVAL_COUNT, dtype=float)
    
    # Downsample the trace to the profile array
    for i in xrange(PROFILE_INTERVAL_COUNT):
        start = readings_to_aggregate * i
        end = min(readings_to_aggregate * (i + 1), len(trace_ts))
        
        # ATTENTION: Using mean here
        profile[i] = np.mean(trace_ts[start:end])
        
    # Calculate interval
    interval = EXPERIMENT_DURATION / PROFILE_INTERVAL_COUNT
        
    # Save the profile
    if save:
        connection = times_client.connect()
        __write_profile(connection, name + POSTFIX_TRACE, profile, interval)
        times_client.close()
    
def plot_overlay_mix():
    '''
    Plots all TS of a mix in a single axis graph
    '''
    # Connect with times
    connection = times_client.connect()
    
    plot_mix = mix_1
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    import random
    for i in xrange(0, 5):
        i = random.randint(0, len(plot_mix) - 1)
        desc = plot_mix[i]
        
        name = desc.name
        timeSeries = connection.load(name + POSTFIX_USER)
        _, demand = util.to_array(timeSeries)
        
        ax.plot(range(0, len(demand)), demand, linewidth=0.7)

    plot.rstyle(ax)
    plt.savefig(configuration.path('overlay', 'png'))
    plt.savefig(configuration.path('overlay', 'pdf'))
    
    # Close times connection
    times_client.close()
    
    
def __plot_complete_mix():
    '''
    Plots all TS of a mix in a single image using multiple axis
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

    plt.savefig(configuration.path('mix_overlay', 'png'))
    
    # Close times connection
    times_client.close()


def dump(logger):
    logger.info('selected_name = %s' % selected_name)
    
    
def dump_user_profile_maxes():
    '''
    Used to verify that all user profiles have user values below MAX_USERS
    '''
    # Connect with times
    connection = times_client.connect()
    
    for name in connection.find('.*%s$' % (POSTFIX_USER)):
        result = util.to_array(connection.load(name))[1]
        if np.max(result) > MAX_USERS: 
            print '%s - %i' % (name, np.max(result))
    
    times_client.close()
    
    
# Builds the profiles and saves them in Times
def main():
    # dump_user_profile_maxes()
    # build_modified_profiles(selected, True)
    # plot_overlay_mix()
    # build_all_profiles_for_mix(selected, False)
    pass

if __name__ == '__main__':
    main()
