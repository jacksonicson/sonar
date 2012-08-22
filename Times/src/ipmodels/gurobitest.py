from gurobipy import *

server_count = 3
service_count = 5
load = [50,30,30,20,50]
server_limit = 100

allocation_matrix = None
servers_active = None

def createVariables(model):
    # Server active variables
    global allocation_matrix
    global servers_active
    
    servers_active = []
    for i in xrange(0, server_count):
        v = model.addVar(vtype=GRB.BINARY, name="server_active_%i" % (i))
        servers_active.append(v); 
        
    # Allocation matrix variables
    allocation_matrix = [[0 for _ in xrange(0, service_count)] for _ in xrange(0, server_count)]
    for i in xrange(0, server_count): 
        for j in xrange(0, service_count):
            v = model.addVar(vtype=GRB.BINARY, name="allocation_%i_%i" % (i, j))
            allocation_matrix[i][j] = v 
    
    model.update()
    

def setupConstraints(model):
    # Allocate all services constraint
    for j in xrange(0, service_count):
        model.addConstr(quicksum(allocation_matrix[i][j] for i in xrange(0, server_count)) == 1.0, 'test')
        
    # Limit server capacity constraint
    for i in xrange(0, server_count):
        server_load = quicksum((load[j] * allocation_matrix[i][j]) for j in xrange(0, service_count))
        model.addConstr(server_load <= (servers_active[i] * server_limit))
        
    model.update()
     
    
    model.setObjective(quicksum(servers_active[i] for i in xrange(0, server_count)), GRB.MINIMIZE)
     
    model.update()


model = Model("ssap"); 
createVariables(model)
setupConstraints(model) 
model.optimize()
print model.getVarByName('server_active_2').x 
for v in model.getVars():
    print v.varName, v.x
    
for v in servers_active:
    print v.x
