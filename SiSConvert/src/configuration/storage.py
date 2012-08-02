import pymongo

connection = pymongo.Connection('192.168.159.1', 27017)
db = connection.dod

allocations = db.allocations
timeseries = db.timeseries
tsdata = db.tsdata
targets = db.targets
suites = db.suites
servers = db.servers
