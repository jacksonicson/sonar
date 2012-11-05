'''
Global Configuration File
'''

from socket import gethostname

# Other configuration files
from virtual import nodes as _nodes #@UnusedImport
from workload import profiles as _profiles #@UnusedImport


##########################
## GLOBAL               ##
PRODUCTION = False

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
