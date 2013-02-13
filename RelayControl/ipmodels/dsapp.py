from gurobipy import *
from numpy import empty

###############################
### Configuration            ##
server_count = None
service_count = None
server_capacity = None
demand_raw = None
demand_mem = None
###############################

def demand(service, resource, time):    # SIGNATUR ANPASSEN
    if resource == 0:
        return demand_raw[service, time]
    else:
        return demand_mem 

def createVariables(model):
    pass

def setupConstraints(model):
    pass

def setupObjective(model):
    pass


def getAssignment():
    pass
    
def getServerCounts():
    pass

# SIGNATUR ANPASSEN
def solve(_server_count, _server_capacity_cpu, _server_capacity_mem, _demand_raw):
    global server_count
    global service_count
    global server_capacity_CPU
    global demand_duration
    global demand_raw
    
    server_count = _server_count
    service_count = len(_demand_raw)
    server_capacity_CPU = _server_capacity_cpu
    demand_duration = len(_demand_raw[0])
    demand_raw = _demand_raw
    
    model = Model("dsapp"); 
    createVariables(model)
    setupConstraints(model) 
    setupObjective(model)
    model.setParam('OutputFlag', False)
    model.optimize()


#TODO create ASSIGNMENT


# Test program
if __name__ == '__main__':
    print "Testing DSAP plus"
    solve(5, 100, 100, _____________)
    print "Testing DSAP plus _finished_"