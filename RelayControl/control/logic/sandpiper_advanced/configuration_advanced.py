######################
## CONFIGURATION    ##
######################
START_WAIT = 120
INTERVAL = 300
THRESHOLD_OVERLOAD = 90
THRESHOLD_UNDERLOAD = 40
PERCENTILE = 80.0
THRESHOLD_IMBALANCE = 0.12
MIN_IMPROVEMENT_IMBALANCE = 0.01
NODE_CAPACITY = 100 #to be checked
K_VALUE = 20 # sliding windows size
M_VALUE = 17 # m values out of the window k must be above or below the threshold

# MIXED CONTROLLER SETTINGS
# Values can be 'imbalance', 'reactive', 'swap' or ''
CONTROLLER_SEQ = ['imbalance', 'reactive', 'swap']
######################
