from gurobipy import *
from numpy import empty, random

###############################
### Configuration            ##
server_count = None
service_count = None
server_capacity = None
demand_duration = None
demand_raw = None
###############################

def demand(service, time):
    return demand_raw[service, time] 

def createVariables(model):
    global var_allocation
    global var_server_active
    
    # Server active flags
    var_server_active = empty((server_count), dtype=object)
    for i in xrange(server_count):
        v = model.addVar(vtype=GRB.BINARY)
        var_server_active[i] = v 
        
    # Allocation flags
    var_allocation = empty((server_count, service_count), dtype=object)
    for i in xrange(server_count): 
        for j in xrange(service_count):
            v = model.addVar(vtype=GRB.BINARY)
            var_allocation[i, j] = v 
    
    model.update()
    

def setupConstraints(model):
    # Allocate all services
    for j in xrange(service_count):
        model.addConstr(quicksum(var_allocation[i, j] for i in xrange(0, server_count)) == 1.0)
        
    # Capacity constraint
    for d in xrange(demand_duration):
        for i in xrange(server_count):
            server_load = quicksum((demand(j, d) * var_allocation[i, j]) for j in xrange(0, service_count))
            model.addConstr(server_load <= (var_server_active[i] * server_capacity))
        
    model.update()


def setupObjective(model):
    expr = quicksum((0,))
    expr += quicksum(var_server_active[i] for i in xrange(0, server_count))
    
    model.setObjective(expr, GRB.MINIMIZE)
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
    
def solve(_server_count, _server_capacity, _demand_raw):
    global server_count
    global service_count
    global server_capacity
    global demand_duration
    global demand_raw
    
    server_count = _server_count
    service_count = len(_demand_raw)
    server_capacity = _server_capacity
    demand_duration = len(_demand_raw[0])
    demand_raw = _demand_raw
    
    model = Model("ssap"); 
    createVariables(model)
    setupConstraints(model) 
    setupObjective(model)
    model.setParam( 'OutputFlag', False )
    model.optimize()
    
    if model.getAttr(GRB.attr.SolCount) > 0:
        return (getServerCount(), getAssignment())
    else:
        return (None, None)

# Test program
if __name__ == '__main__':
    demand_duration = 24
    service_count = 20
    demand_raw = empty((service_count, demand_duration), dtype=float)
    
    # Fill demand with random data
    for j in xrange(service_count):
        for t in range(demand_duration):
            demand_raw[j][t] = random.randint(0, 50)
            
    solve(20, 100, demand_raw)

    


