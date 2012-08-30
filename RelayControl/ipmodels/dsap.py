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
    var_server_active = empty((demand_duration, server_count), dtype=object)
    for d in xrange(demand_duration):
        for i in xrange(server_count):
            v = model.addVar(vtype=GRB.BINARY)
            var_server_active[d, i] = v 
        
    # Allocation flags
    var_allocation = empty((demand_duration, server_count, service_count), dtype=object)
    for d in xrange(demand_duration):
        for i in xrange(server_count): 
            for j in xrange(service_count):
                v = model.addVar(vtype=GRB.BINARY)
                var_allocation[d, i, j] = v 
    
    model.update()
    

def setupConstraints(model):
    # Allocate all services
    for d in xrange(demand_duration):
        for j in xrange(service_count):
            model.addConstr(quicksum(var_allocation[d, i, j] for i in xrange(0, server_count)) == 1.0)
        
    # Capacity constraint
    for d in xrange(demand_duration):
        for i in xrange(server_count):
            server_load = quicksum((demand(j, d) * var_allocation[d, i, j]) for j in xrange(0, service_count))
            model.addConstr(server_load <= (var_server_active[d, i] * server_capacity))
        
    model.update()


def setupObjective(model):
    expr = quicksum((0,))
    for d in xrange(demand_duration):
        expr += quicksum(var_server_active[d, i] for i in xrange(0, server_count))
    
    model.setObjective(expr, GRB.MINIMIZE)
    model.update()


def getAssignment():
    global var_allocation
    
    assignment_list = []
    for d in xrange(demand_duration):
        assignment = {}
        assignment_list.append(assignment)
        
        for j in xrange(service_count):
            for i in xrange(server_count):
                if var_allocation[d, i, j].x > 0.5:
                    assignment[j] = i
                    break
        
    return assignment_list
    
    
def getServerCounts():
    server_counts = [0 for _ in xrange(demand_duration)]
    
    for d in xrange(demand_duration):
        for i in xrange(server_count):
            if var_server_active[d, i].x > 0:
                server_counts[d] += 1
    
    return server_counts
        

def solve(_server_count, _server_capacity, _demand_raw, ):
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
    model.optimize()

    assignment = getAssignment()
    print assignment
    
    server_counts = getServerCounts()
    print server_counts
    

# Test program
if __name__ == '__main__':
    demand_duration = 24
    service_count = 12
    demand_raw = empty((service_count, demand_duration), dtype=float)
    
    # Fill demand with random data
    for j in xrange(service_count):
        for t in range(demand_duration):
            demand_raw[j][t] = random.randint(0, 50)
            
    solve(12, 100, demand_raw)

    


