"""
Das Script wird verwendet, um die SIS CSV-Daten in die MongoDB-Datenbank zu kopieren. 
Von dort werden sie dann ausgelesen und z.B. in den LPs weiterverarbeitet. 
"""
import csv 
import pymongo
import os
import random 

connection = pymongo.Connection()
db = connection.dod
allocations = db.allocations
 
 
def generate_random_allocation(identifier, servers, services):
    
    allocation = []
    for i in range(0, servers):
        allocation.append([])
        
    for j in range(0, services):
        server = random.randint(0, servers - 1)
        allocation[server].append(j)
        
    json_obj = {
                'identifier' : identifier,
                'servers' : servers,
                'services' : services,
                'allocation' : allocation,
                } 
    
    print json_obj
    allocations.save(json_obj)
    
    
if __name__ == '__main__':
    generate_random_allocation('6x6', 6, 6)
    generate_random_allocation('12x12', 12, 12)
    generate_random_allocation('24x24', 24, 24)
    
