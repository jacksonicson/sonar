'''
Global Configuration File
'''

from socket import gethostname
import sys

# Other configuration files
from virtual import nodes as _nodes #@UnusedImport
from workload import profiles as _profiles #@UnusedImport


##########################
## GLOBAL               ##
PRODUCTION = False

# Ask user explicitly if production mode is enabled
__asked = False
if PRODUCTION == True and __asked == False:
    __asked = True
    
    if gethostname() != 'Andreas-PC':
        print 'ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR '
        print 'You hostname is not allowed to launch in production mode'
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
COLLECTOR_IP = 'monitor0'
COLLECTOR_HOST = 'monitor0.dfg'
COLLECTOR_PORT = 7911

##########################
## RELAY    T           ##
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
