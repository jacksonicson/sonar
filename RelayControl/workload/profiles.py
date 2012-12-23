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
import pdata
import util

'''
Configs
'''
class Config(object):
    def __init__(self, prefix, name, data, modified, traces=False):
        self.prefix = prefix
        self.name = name
        self.data = data
        self.modified = modified
        self.traces = traces

mix0 = Config(None, 'mix_0', pdata.mix_0, False, True)
mix1 = Config(None, 'mix_1', pdata.mix_1, False, True)
mix2 = Config(None, 'mix_2', pdata.mix_2, False, True)

mix0m = Config(None, 'mix_0', pdata.mix_0, True, True)
mix1m = Config(None, 'mix_1', pdata.mix_1, True, True)
mix2m = Config(None, 'mix_2', pdata.mix_2, True, True)

mixsim = Config('mix_sim', 'mix_sim', pdata.mix_sim, False)
mixsim2 = Config('mix_sim2', 'mix_sim2', pdata.mix_sim2, False)

##############################
## CONFIGURATION            ##
##############################
config = mixsim2
##############################

##############################
selected_profile = config.prefix    # Prefix for picking TS from Times
selected_name = config.name         # Just for logging
selected = config.data              # Selected workload mix
modified = config.modified          # Modified version of the workload mix
traces_exist = config.traces        # For initial placement profiles traces are used if they exist
##############################

'''
Times file organization:
There are still files with names that do not match the syntax below. These files are
not used by any system at all. 

WORKFLOW 
1) Data gets imported. These TS do not have a PREFIX
2) Data gets processed. The resulting TS are PREFIXed with the name of the MIX

1) IMPORT
[SIS_$NUMBER_mem] - SIS TS for memory
[SIS_$NUMBER_CPU] - SIS TS for CPU
[O2_business_$TYPE] - O2 Business TS with given type
[O2_retail_$TYPE] - O2 Retail TS with given type

2) PROCESSING
[TS] = Imported SIS or O2 TS

[PX][TS]__times_name - RAW workload profiles with convolution (y-axis is not scaled)
[PX][TS]_sampleday -  RAW workload profiles with sampleday (y-axis is not scaled)

[PX][TS]_profile_norm - Normalized workload profile (y-axis is scaled)
[PX][TS][_profile_norm]_modified - Modified normalized workload profile
 
[PX][TS]_profile_user - User profile - normalized workload profile multiplied which maximum users
[PX][TS][_profile_user]_modified - Modified normalized user profile

[PX][TS]_profile_trace - User profiles was executed and the resulting CPU load was logged

The interval of _profile_user is updated so that the length of the TS multiplied 
with the interval matches the EXPERIMENT_DURATION. 
'''

'''
Prefix and post-fixes used to store data in Times
'''
POSTIFX_ORIG = '' # original RAW time series imported from the SIS or O2 data set. This is NO profile!!!
POSTFIX_RAW = 'profile' # profile generated from the raw data of the SIS or O2 data set 
POSTFIX_NORM = 'profile_norm' # Normalized profile against the set maximum, see mix_selected and ProfileSet class
POSTFIX_USER = 'profile_user' # Normalized profile multiplied with the max. number of users
POSTFIX_DAY = 'sampleday' # A sample day of the time series
POSTFIX_TRACE = 'profile_trace' # Recorded profile which resulted using the user profile in the load driver
POSTFIX_MODIFIED = 'modified' # A modified trace

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


def get_current_cpu_profile(index):
    '''
    Gets CPU profile by index from the selected workload mix. The selection
    depends on the modified flag. 
    '''
    desc = __by_index(index)
    if modified:
        name = __times_name(True, desc.name, POSTFIX_NORM, POSTFIX_MODIFIED)
    else:
        name = __times_name(True, desc.name, POSTFIX_NORM)
        
    print 'Selected cpu profile: %s' % name
    return name

def get_cpu_profile_for_initial_placement(index):
    '''
    Gets a traced CPU profile by index from the selected workload mix. The selection
    depends on the modified flag. 
    '''
    if traces_exist:
        desc = __by_index(index)
        name = __times_name(True, desc.name, POSTFIX_TRACE)
    else:
        name = get_current_cpu_profile(index)
    
    print 'Selected CPU profile for initial placement: %s' % name
    return name

def get_current_user_profile(index):
    '''
    Gets user profile by index from the selected workload mix. The selection
    depends on the modified flag. 
    '''
    desc = __by_index(index)
    if modified:    
        name = __times_name(True, desc.name, POSTFIX_USER, POSTFIX_MODIFIED)
    else:
        name = __times_name(True, desc.name, POSTFIX_USER)
        
    print 'Selected user profile: %s' % name
    return name 

         
def __times_name(prefixed, *args):
    if prefixed:
        if selected_profile is None:
            name = ''
        else:
            name = selected_profile + '_'
    else:
        name = ''
             
    name += '_'.join(args)
    return name


def __by_index(index):
    '''
    Get TS description by index
    '''
    return selected[index]


def __write_profile(connection, name, profile_ts, interval, overwrite=True, noprefix=False):
    '''
    Saves a TS in the Times service.
    
    Keyword arguments:
    connection -- The connection as returned by the Times client
    name -- Name of the TS
    profile_ts -- A numpy array which contains the elements of the TS
    interval -- The time delta between two data points in the profile_ts TS (in seconds) 
    '''
    
    # Extend name with the current workload mix prefix
    if not noprefix and selected_profile is not None:
        if name.find(selected_profile) != 0:
            if not selected_profile:
                name = selected_profile + '_' + name
    
    # Check if the profile exists
    if len(connection.find(name)) > 0:
        # Double check if it is allowed to overwrite profiles in Times
        if overwrite:
            print 'removing existing data file'
            connection.remove(name)
        else:
            print 'return - will not overwrite profile %s' % name
            return
        
    # Store profile
    print 'STORING - Identifier for profile in Times: %s' % (name)
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
        __write_profile(connection, __times_name(True, desc.name, POSTFIX_RAW), raw_profile, interval)
    
    # Store NORMALIZED profiles (normalized with the set maximum, see above) (-> feed into SSAPv)
    maxval = float(set_max[pset.id])
    profile /= maxval
    norm_profile = np.array(profile)
    norm_profile[norm_profile > 1] = 1
    norm_profile *= 100 # Times does not support float values
    if save:
        __write_profile(connection, __times_name(True, desc.name, POSTFIX_NORM), norm_profile, interval)
    
    # Store USER profiles (-> feed into Rain)
    # - Adapt interval for the benchmark duration
    # - Add padding for ramp up and ramp down
    profile *= MAX_USERS
    interval = interval / (CYCLE_TIME / EXPERIMENT_DURATION)
    user_profile = np.array(profile)
    user_profile = __padprofile(user_profile, interval)
    
    if np.max(user_profile) > MAX_USERS:
        print '%s > max users - %i' % (__times_name(True, desc.name, POSTFIX_USER), np.max(user_profile))
        
    if save:
        __write_profile(connection, __times_name(True, desc.name, POSTFIX_USER), user_profile, interval)
    
    # Plotting    
    # util.plot(user_profile, desc.name + '.png', MAX_USERS)


def __build_sample_day(mix, save):
    connection = times_client.connect()

    # Calculate profiles
    for desc in mix:
        print 'processing sample day %s' % (desc.name)
        import sampleday
        profile = sampleday.process_trace(connection, __times_name(False, desc.name),
                                          desc.sample_frequency, CYCLE_TIME, desc.profile_set.day)
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
        # Operates on pre-processed data. Hence, a prefix is required
        ts_name = __times_name(True, mi_element.name, POSTFIX_NORM)

        # Modify CPU normal profile     
        modified_profile, interval = modifier.process_trace(connection, ts_name,
                                                            mi_element.modifier, mi_element.additive,
                                                            mi_element.scale, mi_element.shift)
        if save:
            name = __times_name(True, mi_element.name, POSTFIX_NORM, POSTFIX_MODIFIED)
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
            name = __times_name(True, mi_element.name, POSTFIX_NORM, POSTFIX_MODIFIED)
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
        profile = convolution.process_trace(connection, __times_name(False, desc.name),
                                            desc.sample_frequency, CYCLE_TIME)
        
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
        
        if set_max.has_key(pset.id) == False:
            set_max[pset.id] = 0
            
        max_value = np.percentile(profile_ts, 95)
        set_max[pset.id] = max(max_value, set_max[pset.id])
        if pset.cap:
            set_max[pset.id] = min(pset.cap, set_max[pset.id])
            
    return set_max


def __padprofile(profile_ts, interval):
    '''
    Each benchmark runs a ramp-up and a ramp-down phase. The profile used by Rain needs
    to be extended so that it contains data to cover the ramp-up and ramp-down phases. 
    '''
    
    # Number of elements for ramp-up 
    # print 'padding ramp up: %i' % (elements)
    elements = RAMP_UP / interval
    ramup_pad = np.zeros(elements, np.float)
    mean = np.mean(profile_ts)
    ramup_pad[range(elements)] = mean
    
    # Number of elements for ramp-down
    # print 'padding ramp down: %i' % (elements)
    elements = RAMP_DOWN / interval
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
        # Special case - no prefix is added as this TS is treated as a RAW TS
        __write_profile(connection, __times_name(False, name, POSTFIX_TRACE), profile, interval, noprefix=True)
        times_client.close()
    
def dump_to_csv():
    connection = times_client.connect()
    
    demands = []
    for desc in selected:
        timeSeries = connection.load(__times_name(True, desc.name, POSTFIX_NORM))
        _, demand = util.to_array(timeSeries)
        demands.append((desc.name, demand))
        
    import csv
    with open(configuration.path('traces', 'csv'), 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter='\t')
        
        row = []
        for demand in demands:
            row.append(demand[0])
        spamwriter.writerow(row)
        
        l = len(demands[0][1])
        for i in xrange(0, l):
            row = []
            for demand in demands:
                if i < len(demand[1]): 
                    row.append(demand[1][i])
                else:
                    print 'warn'
                    row.append(0)
                    
            spamwriter.writerow(row)
        
    times_client.close()
    
def plot_overlay_mix():
    '''
    Plots all TS of a mix in a single axis graph
    '''
    # Connect with times
    connection = times_client.connect()
    
#    mix0 = ['O2_retail_ADDORDER', 'SIS_163_cpu', 'SIS_393_cpu']
#    mix1 = ['SIS_222_cpu', 'SIS_213_cpu', 'SIS_387_cpu']
#    plot_mix = mix0
    a = 0
    
    plot_mix = []
    for i in xrange(a, a+100):
        print selected[i].name
        plot_mix.append(selected[i].name)
    
    fig = plt.figure()
    
    ax = fig.add_subplot(111)
    ax.set_xlim([0, 300])
    
    for name in plot_mix:
        timeSeries = connection.load(__times_name(True, name, POSTFIX_NORM))
        _, demand = util.to_array(timeSeries)
        
        ax.plot(range(0, len(demand)), demand, linewidth=0.7)

    
    ax.set_xlabel('Time x5 minutes')
    ax.set_ylabel('Load in number of users')
    
    plt.show()
#    plt.savefig(configuration.path('overlay', 'png'))
#    plt.savefig(configuration.path('overlay', 'pdf'))
    
    # Close times connection
    times_client.close()
    
    
def __plot_complete_mix():
    '''
    Plots all TS of a mix in a single image using multiple axis
    '''
    
    # Connect with times
    connection = times_client.connect()
    
    plot_mix = pdata.mix_2
    cols = 5
    rows = len(plot_mix) / cols + 1 
    index = 0
    print rows
    
    fig = plt.figure()
    fig.set_figheight(20)
    fig.set_figwidth(40)
    
    for desc in plot_mix:  
        name = desc.name
        timeSeries = connection.load(__times_name(True, name, POSTFIX_USER))
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
    build_all_profiles_for_mix(selected, True)
    # build_modified_profiles(selected, False)
    plot_overlay_mix()
    # dump_to_csv()
    pass

if __name__ == '__main__':
    main()
