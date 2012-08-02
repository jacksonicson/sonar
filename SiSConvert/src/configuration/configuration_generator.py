import random
import storage
import time
import update
import configuration_helpers as ch

def get_servers(length):
    # Create a sample of servers
    servers = []
    for s in range(0, length):
        servers.append('paper1_1')
    return servers


def get_SIS_traces():
    # Generate names of all traces
    name_traces = []
    for i in range(160, 200):
        name = '/tmp/SIS RAW/%s' % i
        name_traces.append(name)
        
    return name_traces


def get_O2_traces():
    # Generate names of all traces
    name_traces = []
    for i in range(0, 16):
        name = '/tmp/O2 RAW business/%s' % i
        name_traces.append(name)
        
    for i in range(0, 16):
        name = '/tmp/O2 RAW retail/%s' % i
        name_traces.append(name)
      
    return name_traces


def random_traces(length, name_traces=get_O2_traces()):
    # Pick a sample of traces
    traces = []
    for i in range(0, length):
        value = name_traces[random.randint(0, len(name_traces) - 1)]
        name_traces.remove(value)
        traces.append(value)
    
    return traces


def write_ant_properties_file(suite):
    file = open('ant.properties', 'w')
    file.write('suite:%s' % (suite))
    file.close()


def main():
    number = int(time.time())
    suite = 'configuration%s' % (number)
    text = 'Nothing'
    labels = ['DSAP+', 'TEMP']
    
    # Create suite
    suite_id = ch.create_suite(suite, text, labels)
    if suite_id is None:
        print 'unable to create suite %s' % (suite)
        return

    # Update properties file which is used in Apache ANT to start the simulation
    write_ant_properties_file(suite); 
   
    # Create targets for this suite    
    num_servers = 10
    num_services = 15
    overheads = [(0.4, 0.2)]
    timesteps = 24

    for run in range(0,1):    
        traces = random_traces(num_services)
        servers = get_servers(num_servers)
    
        for lookahead in range(20, 25):
            for overhead in overheads: 
                overhead_out = overhead[0]
                overhead_in = overhead[1]
             
                # Create an allocation sequence with the DSAP+
                ch.write_configuration_dsapps(suite, suite_id, timesteps, lookahead, traces, servers,
                                          None, overhead_out, overhead_in, depends=[])
            
    ###########################

    # Set all targets waiting
    update.update_targets(suite, 'waiting') 
    

if __name__ == '__main__':
    main()
