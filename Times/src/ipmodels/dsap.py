from gurobipy import *

server_count = 3
service_count = 5
load_length = 1
load = [50,30,30,20,50]
server_limit = 100

allocation_matrix = None
servers_active = None

def createVariables(model):
    # Server active variables
    global allocation_matrix
    global servers_active
    
    import numpy as np
    servers_active = np.empty([load_length, server_count], dtype=object)
    allocation_matrix = np.empty([load_length, server_count, service_count], dtype=object)
    
    for t in xrange(0, load_length):
        for i in xrange(0, server_count):
            v = model.addVar(vtype=GRB.BINARY, name="server_active_%i_%i" % (t, i))
            servers_active[t, i] = v 
        
    # Allocation matrix variables
    for t in xrange(0, load_length):
        for i in xrange(0, server_count): 
            for j in xrange(0, service_count):
                v = model.addVar(vtype=GRB.BINARY, name="allocation_%i_%i_%i" % (t, i, j))
                allocation_matrix[t, i, j] = v 
    
    model.update()
    

def setupConstraints(model):
    # Allocate all services in all time slots constraint
    for t in xrange(0, load_length):
        for j in xrange(0, service_count):
            model.addConstr(quicksum(allocation_matrix[t][i][j] for i in xrange(0, server_count)) == 1.0, 'test')
        
    # Limit server capacity in all time slots constraint
    for t in xrange(0, load_length):
        for i in xrange(0, server_count):
            server_load = quicksum((load[j] * allocation_matrix[t][i][j]) for j in xrange(0, service_count))
            model.addConstr(server_load <= (servers_active[t][i] * server_limit))
        
    model.update()
     
    term = quicksum((0,))
    for t in xrange(0, load_length):
        s = quicksum(servers_active[t][i] for i in xrange(0, server_count))
        term += s
    model.setObjective(term, GRB.MINIMIZE)
     
    model.update()


model = Model("ssap"); 
createVariables(model)
setupConstraints(model) 
model.optimize()
 
for v in model.getVars():
    print v.varName, v.x
    

