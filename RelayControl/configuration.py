'''
Global Configuration File
'''

from socket import gethostname

##########################
## COLLECTOR            ##
COLLECTOR_IP = 'monitor0'
COLLECTOR_HOST = 'monitor0.dfg'
COLLECTOR_PORT = 7911

##########################
## LOGGING              ##
SONAR_LOGGING = False
LOGGING_PORT = 7921
HOSTNAME = gethostname()

##########################
## CONTROLLER           ##
PRODUCTION = False
LISTENING_PORT = 9876
LISTENING_INTERFACE_IPV4 = '192.168.96.6'

##########################
## RELAY    T           ##
RELAY_PORT = 7900
