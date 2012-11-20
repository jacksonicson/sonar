from gurobipy import *
from numpy import empty

###############################
### Configuration            ##
server_count = None
service_count = None
server_capacity = None
demand_raw = None
###############################

def demand(service):
    return demand_raw[service] 

def createVariables(model):
    global var_allocation
    global var_server_active
    
    # Server active flags
    var_server_active = empty((server_count), dtype=object)
    print type(var_server_active)
    for i in xrange(0, server_count):
        v = model.addVar(vtype=GRB.BINARY)
        var_server_active[i] = v 
        
    # Allocation flags
    var_allocation = empty((server_count, service_count), dtype=object)
    for i in xrange(0, server_count): 
        for j in xrange(0, service_count):
            v = model.addVar(vtype=GRB.BINARY)
            var_allocation[i][j] = v 
    
    model.update()
    

def setupConstraints(model):
    # Allocate all services
    for j in xrange(0, service_count):
        model.addConstr(quicksum(var_allocation[i][j] for i in xrange(0, server_count)) == 1.0)
        
    # Capacity constraint
    for i in xrange(0, server_count):
        server_load = quicksum((demand(j) * var_allocation[i][j]) for j in xrange(0, service_count))
        model.addConstr(server_load <= (var_server_active[i] * server_capacity))
        
    model.update()


def setupObjective(model):
    model.setObjective(quicksum(var_server_active[i] for i in xrange(0, server_count)), GRB.MINIMIZE)
    model.update()


def getAssignment():
    global var_allocation
    
    assignment = {}
    for j in xrange(0, service_count):
        for i in xrange(0, server_count):
            if var_allocation[i][j].x > 0.5:
                assignment[j] = i
                break
        
    return assignment
        
def getServerCount():
    count = 0
    for i in xrange(server_count):
        if var_server_active[i].x > 0:
            count += 1
    return count

def solve(_server_count, _server_capacity, _demand):
    global server_count
    global service_count
    global server_capacity
    global demand_raw
    
    server_count = _server_count
    service_count = len(_demand)
    server_capacity = _server_capacity
    demand_raw = _demand  
    
    model = Model("ssap"); 
    createVariables(model)
    setupConstraints(model) 
    setupObjective(model)
    model.optimize()

    assignment = getAssignment()
    print assignment
    
    server_count = getServerCount()
    print server_count

# Test program
if __name__ == '__main__':
    solve(5, 100, [30, 2, 33, 44, 66])

    
