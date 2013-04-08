'''
Global Configuration File
'''

from socket import gethostname
import sys

'''
Configuring a benchmark run: 
- Check settings in nodes
- Check settings in profiles (all configuration parameters)
- Check settings in domains
- Check settings in control.allocate_domains
- Run initial allocation 
- Check configuration of Controller: control.logic.controller <I-- subclasses
- Check Controller reference: control.logic.main.py
- Check start_benchmark.py configuration
'''

# Other configuration files
# @see virtual.nodes
# @see workload.profiles
# @see control.domains

##########################
## GLOBAL               ##
PRODUCTION = False

# Ask user explicitly if production mode is enabled
__asked = False
if PRODUCTION == True and __asked == False:
    __asked = True
    
    if gethostname() != 'Andreas-PC':
        print 'ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR '
        print 'You hostname %s is not allowed to launch in production mode' % gethostname()
        print 'ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR '
        sys.exit(0)
    
    print 'WARNING WARNING WARNING WARNING WARNING WARNING WARNING'
    print 'Production mode is set to TRUE'
    print 'WARNING WARNING WARNING WARNING WARNING WARNING WARNING'
    yes = raw_input('Enter "y" to continue:')
    if yes != 'y':
        print 'Exiting'
        sys.exit(0);

##########################
## COLLECTOR            ##
COLLECTOR_IP = 'monitor0.dfg'
COLLECTOR_HOST = 'monitor0.dfg'
COLLECTOR_PORT = 7911

##########################
## RELAY                ##
RELAY_PORT = 7900

##########################
## LOGGING              ##
# Logging to Sonar is only enabled in production mode. Everything else
# is debugging or playground tests. 
SONAR_LOGGING = PRODUCTION
LOGGING_PORT = 7921
HOSTNAME = gethostname()

##########################
## CONTROLLER           ##
LISTENING_PORT = 9876
LISTENING_INTERFACE_IPV4 = '192.168.96.6'
PUMP_SPEEDUP = 1
MIGRATION_DOWNTIME = 15000

##########################
## IAAS                 ##
IAAS_PORT = 9877 
IAAS_INTERFACE_IPV4 = '192.168.96.6'

##########################
## FILES                ##
def path(filename, ending='txt'):
    return 'C:/temp/%s.%s' % (filename, ending)
