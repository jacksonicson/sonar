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

[PX][TS]_profile - RAW workload profiles with convolution (y-axis is not scaled)
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
PREFIX_MIX_SIM = 'mix_sim'

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

class Desc:
    '''
    Describes a single TS which is used to generate a profile
    '''
    def __init__(self, name, profile_set, modifier=modifier.MOD0, scale=(1, 1), shift=0, additive=0):
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
        self.ifreq = ifreq
        self.cap = cap
        self.day = day


# List of profile sets
SET_O2_BUSINESS = ProfileSet(0, hour(1), None)
SET_O2_RETAIL = ProfileSet(1, hour(1), None)
SET_SIS = ProfileSet(2, minu(5), 3000)

# List of profile days
SET_SIS_D3 = ProfileSet(3, minu(5), 3000, day=3)
SET_SIS_D8 = ProfileSet(3, minu(5), 3000, day=8)
SET_SIS_D9 = ProfileSet(3, minu(5), 3000, day=9)
SET_SIS_D10 = ProfileSet(3, minu(5), 3000, day=10)
SET_SIS_D26 = ProfileSet(3, minu(5), 3000, day=26)

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

# MIX Simulation
mix_sim = [
            Desc('O2_business_ADDORDER', SET_O2_BUSINESS, modifier.MOD8, (1.2, 1), minu(10), 20),
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
            
            Desc('SIS_207_cpu', SET_SIS_D10),
            Desc('SIS_208_cpu', SET_SIS_D10),
            Desc('SIS_210_cpu', SET_SIS_D10),
            Desc('SIS_211_cpu', SET_SIS_D10),
            Desc('SIS_213_cpu', SET_SIS_D10),
            Desc('SIS_214_cpu', SET_SIS_D10),
            Desc('SIS_216_cpu', SET_SIS_D10),
            Desc('SIS_219_cpu', SET_SIS_D10),
            Desc('SIS_220_cpu', SET_SIS_D10),
            Desc('SIS_221_cpu', SET_SIS_D10),
            Desc('SIS_222_cpu', SET_SIS_D10),
            Desc('SIS_223_cpu', SET_SIS_D10),
            Desc('SIS_225_cpu', SET_SIS_D10),
            Desc('SIS_234_cpu', SET_SIS_D10),
            Desc('SIS_235_cpu', SET_SIS_D10),
            Desc('SIS_243_cpu', SET_SIS_D10),
            Desc('SIS_245_cpu', SET_SIS_D10),
            Desc('SIS_264_cpu', SET_SIS_D10),
            Desc('SIS_269_cpu', SET_SIS_D10),
            Desc('SIS_270_cpu', SET_SIS_D10),
            Desc('SIS_271_cpu', SET_SIS_D10),
            Desc('SIS_275_cpu', SET_SIS_D10),
            Desc('SIS_279_cpu', SET_SIS_D10),
            Desc('SIS_312_cpu', SET_SIS_D10),
            Desc('SIS_315_cpu', SET_SIS_D10),
            Desc('SIS_328_cpu', SET_SIS_D10),
            Desc('SIS_385_cpu', SET_SIS_D10),
            Desc('SIS_386_cpu', SET_SIS_D10),
            Desc('SIS_387_cpu', SET_SIS_D10),
            
            Desc('SIS_21_cpu', SET_SIS_D26),
            Desc('SIS_24_cpu', SET_SIS_D26),
            Desc('SIS_27_cpu', SET_SIS_D26),
            Desc('SIS_29_cpu', SET_SIS_D26),
            Desc('SIS_31_cpu', SET_SIS_D26),
            Desc('SIS_110_cpu', SET_SIS_D26),
            Desc('SIS_145_cpu', SET_SIS_D26),
            Desc('SIS_147_cpu', SET_SIS_D26),
            Desc('SIS_150_cpu', SET_SIS_D26),
            Desc('SIS_162_cpu', SET_SIS_D26),
            Desc('SIS_209_cpu', SET_SIS_D26),
            Desc('SIS_210_cpu', SET_SIS_D26),
            Desc('SIS_236_cpu', SET_SIS_D26),
            Desc('SIS_243_cpu', SET_SIS_D26),
            Desc('SIS_252_cpu', SET_SIS_D26),
            Desc('SIS_253_cpu', SET_SIS_D26),
            Desc('SIS_272_cpu', SET_SIS_D26),
            Desc('SIS_373_cpu', SET_SIS_D26),
            
            Desc('SIS_298_cpu', SET_SIS),
            Desc('SIS_305_cpu', SET_SIS),
            Desc('SIS_303_cpu', SET_SIS),
            Desc('SIS_309_cpu', SET_SIS),
            Desc('SIS_210_cpu', SET_SIS),
            Desc('SIS_213_cpu', SET_SIS),
            Desc('SIS_314_cpu', SET_SIS),
            Desc('SIS_240_cpu', SET_SIS),
            Desc('SIS_374_cpu', SET_SIS),
            Desc('SIS_393_cpu', SET_SIS),
            Desc('SIS_294_cpu', SET_SIS),
            Desc('SIS_197_cpu', SET_SIS),
            
            Desc('O2_business_ADDORDER', SET_O2_BUSINESS, modifier.MOD3, (1.2, 1), minu(10), 20),
            Desc('O2_business_ADDLINEORDER', SET_O2_BUSINESS, modifier.MOD1),
            Desc('O2_business_CONTRACTEXT', SET_O2_BUSINESS, modifier.MOD3),
            Desc('O2_business_SENDMSG', SET_O2_BUSINESS, modifier.MOD2),
            Desc('O2_business_UPDATEACCOUNT', SET_O2_BUSINESS, modifier.MOD4),
            Desc('O2_business_UPDATEDSS', SET_O2_BUSINESS, modifier.MOD3),
           ]

##############################
## CONFIGURATION            ##
##############################
selected_profile = None # Prefix for picking TS from Times
selected_name = 'mix_1' # Just for logging
selected = mix_1        # Selected workload mix
modified = False        # Modified version of the workload mix
##############################

def _profile(prefixed, *args):
    name = ''
    
    if selected_profile is None:
        prefix = ''
    else:
        prefix = selected_profile + '_'
    
    if prefixed: name = prefix + name
    for arg in args:
        name += arg
    return name

def get_current_cpu_profile(index):
    '''
    Gets CPU profile by index from the selected workload mix. The selection
    depends on the modified flag. 
    '''
    desc = __by_index(index)
    if modified:
        name = _profile(True, desc.name, POSTFIX_NORM, POSTFIX_MODIFIED)
    else:
        name = _profile(True, desc.name, POSTFIX_NORM)
        
    print 'Selected cpu profile: %s' % name
    return name

def get_traced_cpu_profile(index):
    '''
    Gets a traced CPU profile by index from the selected workload mix. The selection
    depends on the modified flag. 
    '''
    if not configuration.PRODUCTION:
        return get_current_cpu_profile(index)    
    
    desc = __by_index(index)
    name = _profile(True, desc.name, POSTFIX_TRACE)
    
    print 'Selected cpu profile: %s' % name
    return name

def get_current_user_profile(index):
    '''
    Gets user profile by index from the selected workload mix. The selection
    depends on the modified flag. 
    '''
    desc = __by_index(index)
    if modified:
        name = _profile(True, desc.name, POSTFIX_USER, POSTFIX_MODIFIED)
    else:
        name = _profile(True, desc.name, POSTFIX_USER)
        
    print 'Selected user profile: %s' % name
    return name 
         

def __by_index(index):
    '''
    Get TS description by index
    '''
    return selected[index]


def __write_profile(connection, name, profile_ts, interval, overwrite=False, noprefix=False):
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
        __write_profile(connection, _profile(True, desc.name, POSTFIX_RAW), raw_profile, interval)
    
    # Store NORMALIZED profiles (normalized with the set maximum, see above) (-> feed into SSAPv)
    maxval = float(set_max[pset.id])
    profile /= maxval
    norm_profile = np.array(profile)
    norm_profile *= 100 # Times does not support float values
    if save:
        __write_profile(connection, _profile(True, desc.name, POSTFIX_NORM), norm_profile, interval)
    
    # Store USER profiles (-> feed into Rain)
    # - Adapt interval for the benchmark duration
    # - Add padding for ramp up and ramp down
    profile *= MAX_USERS
    interval = interval / (CYCLE_TIME / EXPERIMENT_DURATION)
    user_profile = np.array(profile)
    user_profile = __padprofile(user_profile, interval)
    
    if np.max(user_profile) > MAX_USERS:
        print '%s > max users - %i' % (_profile(True, desc.name, POSTFIX_USER), np.max(user_profile))
        
    if save:
        __write_profile(connection, _profile(True, desc.name, POSTFIX_USER), user_profile, interval)
    
    # Plotting    
    util.plot(user_profile, desc.name + '.png', MAX_USERS)


def __build_sample_day(mix, save):
    connection = times_client.connect()

    # Calculate profiles
    for desc in mix:
        print 'processing sample day %s' % (desc.name)
        import sampleday
        profile = sampleday.process_trace(connection, _profile(False, desc.name),
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
        ts_name = _profile(True, mi_element.name, POSTFIX_NORM)

        # Modify CPU normal profile     
        modified_profile, interval = modifier.process_trace(connection, ts_name,
                                                            mi_element.modifier, mi_element.additive,
                                                            mi_element.scale, mi_element.shift)
        if save:
            name = _profile(True, mi_element.name, POSTFIX_NORM, POSTFIX_MODIFIED)
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
            name = _profile(True, mi_element.name, POSTFIX_NORM, POSTFIX_MODIFIED)
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
        profile = convolution.process_trace(connection, _profile(False, desc.name),
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
            
        max_value = np.max(profile_ts)
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
        __write_profile(connection, _profile(False, name, POSTFIX_TRACE), profile, interval, noprefix=True)
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
        timeSeries = connection.load(_profile(True, name, POSTFIX_USER))
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
        timeSeries = connection.load(_profile(True, name, POSTFIX_USER))
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
    build_modified_profiles(selected, True)
    # plot_overlay_mix()
    pass

if __name__ == '__main__':
    main()
