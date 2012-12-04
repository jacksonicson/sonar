from gurobipy import *
from numpy import empty, random
import numpy as np

###############################
### Configuration            ##
server_count = None
service_count = None
server_capacity_CPU = None
server_capacity_MEM = None
demand_duration = None
demand_raw = None
demand_mem = None
###############################

CPU = 0
MEM = 1

def demand(service, resource, time):
    if resource == 0:
        return demand_raw[service, time]
    else:
        return demand_mem 

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
            server_load = quicksum((demand(j, CPU, d) * var_allocation[d, i, j]) for j in xrange(0, service_count))
            model.addConstr(server_load <= (var_server_active[d, i] * server_capacity_CPU))
          
            server_load = quicksum((demand(j, MEM, d) * var_allocation[d, i, j]) for j in xrange(0, service_count))
            model.addConstr(server_load <= (var_server_active[d, i] * server_capacity_MEM))
    
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


def solve(_server_count, _server_capacity_cpu, _server_capacity_mem, _demand_raw, _demand_mem):
    global server_count
    global service_count
    global server_capacity_CPU
    global server_capacity_MEM
    global demand_duration
    global demand_raw
    global demand_mem
    
    server_count = _server_count
    service_count = len(_demand_raw)
    server_capacity_CPU = _server_capacity_cpu
    server_capacity_MEM = _server_capacity_mem
    demand_duration = len(_demand_raw[0])
    demand_raw = _demand_raw
    demand_mem = _demand_mem
    
    model = Model("dsap"); 
    createVariables(model)
    setupConstraints(model) 
    setupObjective(model)
    model.setParam('OutputFlag', False)
    model.optimize()

    assignment_list = getAssignment()
    i = 0
    for interval in assignment_list: 
        print '%i: %s' % (i, interval)
        i += 1
    
    server_counts = getServerCounts()
    print 'Servers per interval: %s' % server_counts
    print 'Average server count: %f' % (np.mean(server_counts))
    
    return server_counts, assignment_list    
    
    
    
# Test program
if __name__ == '__main__':
    demand_duration = 24
    service_count = 12
    demand_raw = empty((service_count, demand_duration), dtype=float)
    
    # A) Fill demand values with random data
    for j in xrange(service_count):
        for t in range(demand_duration):
            demand_raw[j][t] = random.randint(0, 50)
            
    demand_mem = [[] for _ in xrange(len(demand_raw))]
    for i in xrange(len(demand_raw)):
        demand_mem[i] = [0 for _ in xrange(len(demand_raw[i]))]
        
    demand_mem=5
    
    # B) Fill demand values with data from monitor0.dfg (TimeSteps)
    ## see controller_dsap.py
    
#    print demand_mem
#    print demand_raw
    solve(12, 100, 100, demand_raw, demand_mem)
