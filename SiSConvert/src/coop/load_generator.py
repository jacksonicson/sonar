from workload import processor
import matplotlib.pyplot as plt
import random

'''
The burst workload is based on the following parameters
Fire the following query_specification in with given probability
4x  750 warehouses Q1 in 300s
12x 500 warehouses Q2 in 300s
44x 250 warehouses Q3 in 300s
'''


# Compare two query_specification by their offset
def compare_query(x, y):
    return x.offset - y.offset

# Query class
class Query:
    offset = None
    query = None
    slaFinishTime = None
    
    def __init__(self, offset, query_specification, slaFinishTime):
        self.offset = offset
        self.query = query_specification
        self.slaFinishTime = slaFinishTime

    
class WorkloadWrapper:
    query_specification = None
    workload_file = None
    
    def __init__(self, file_handle, query_specification):
        self.workload_file = open(file_handle, 'w')
        self.query_specification = query_specification
    
    
    '''
    Writes the queries to the workload_file handle 
    '''
    def write_queries(self, query_list):
        for i in query_list:
            self.workload_file.write('%i,%i,%i' % (int(i.offset), i.query, i.slaFinishTime))
            self.workload_file.write('\r\n')
    
    
    '''
    Creates a list of queries with count entries and the parameters
    warehouses sla_fiish_time. The offset is determined by a uniformly 
    distributed random number generator within the range [0, wave_time]
    '''
    def build_queries(self, count, warehouses, sla_finish_time, wave_time):
        query_list = []
        
        for i in range(0, int(count)):
            offset = random.uniform(0, wave_time * 1000)
            newQuery = Query(int(offset), warehouses, sla_finish_time)
            
            query_list.append(newQuery) 
            
        return query_list
    
    '''
    Modulate a burst workload with 100% load on the given raw_workload curve. 
    WARN: The burst workload position is hard coded! 
    '''
    def modulate_burst(self, raw_workload):
        for i in range(25, 50):
            raw_workload[i] += 1
            
        return raw_workload
    
    
    '''
    Plot a given raw workload curve. The raw workload has values from 0 to 1. Each
    raw workloaf value is multiplied by the factor to get the number of queries to fire. 
    '''
    def ploat_workload(self, workload, factor, wave_length):
        xvalues = []
        yvalues = []
        
        # Multiply the raw workload by the factor
        offset = 0
        for i in workload:
            yvalues.append(factor * i)
            xvalues.append(offset)
            offset += wave_length

        # Create a new figure        
        fig = plt.figure();
        ax = fig.add_subplot(1, 1, 1)
        
        # Set axes
        ax.set_title("Derived Real World Workload");
        ax.set_xlabel("Time in Seconds"); 
        ax.set_ylabel("Number of Queries"); 
        
        # Plot the figure
        line, = ax.plot(xvalues, yvalues, drawstyle="steps-post")
        line.set_antialiased(False)
        line.set_label("Available - Requested")

        # Save the figure        
        fig.savefig("real workload.pdf", papertype='a4')
    
    
    '''
    Generate a real workload file for the eaware LoadGenerator
    '''
    def generate(self, burst=False):
        # Load the workload from the database
        raw_workload = processor.process_trace('O2 RAW business', str(5))

        # Check if the raw_workload has to be modulated by a burst
        if burst:
            raw_workload = self.modulate_burst(raw_workload)

        
        # RAW workload:
        # Length: 24 hours
        # Each value has a length of 5 minutes (= 300 secs)
        # Burst workload: 0.2 queries per second
        # Burst workload: Max. 60 queries in 300 secs (0.2 q/s * 300s)

        # Real workload (6 hours = 1/4 * 24 hours)        
        interval = 75 # seconds interval 
        peakQueries = 17  # peak queries within one interval

        # Plot the resulting workload
        self.ploat_workload(raw_workload, peakQueries, interval)
        
        # List for all queries in the generated workloads
        total_queries = []
        
        # IMPORTANT:
        # For each value in the raw workload (interval / wave ...)
        for i in raw_workload:
            # Calculate number of queries to fire in this interval
            total_queries_to_fire = max(1, int(peakQueries * i))

            print 'queries in this wave: %i' % (total_queries_to_fire)

            # Calculate the number of queries to fire for each query type
            # given by the query specification
            query_type_count = [0] * len(self.query_specification)
            
            # For each query to fire determine its type
            for i in range(0, total_queries_to_fire):
                # Random value to determine the query type
                random_value = random.random()
                
                # Iterate over each type and check against the random pick
                for j in range(0, len(self.query_specification)):
                    if random_value < self.query_specification[j][0]:
                        # Query type found
                        query_type_count[j] += 1
                        break
                    
                    else:
                        # Decrement random value
                        random_value -= self.query_specification[j][0]
        
        
            # Build the query list
            query_list = []     
            for i in range(0, len(query_type_count)):
                tmp_list = self.build_queries(query_type_count[i], self.query_specification[i][1], self.query_specification[i][2], interval)
                query_list.extend(tmp_list)

            # Sort the list by offset
            query_list.sort(cmp=compare_query, key=None, reverse=False)
            
            # Fix offsets of the query_type_count (absolute to relative offsets within the interval!!!)
            lastOffset = 0
            sumOffsets = 0 
            for query in query_list:
                tmp = query.offset
                query.offset = query.offset - lastOffset
                lastOffset = tmp
                
                sumOffsets += query.offset

            # Insert dummy wait offset to ensure that the interval is complete)
            if (interval * 1000) > sumOffsets:
                query = Query((interval * 1000) - sumOffsets, 0, 999000)
                query_list.append(query)
                sumOffsets += query.offset

            # Add the queries for this intervals to the total_queries list
            total_queries.extend(query_list)
            
            
        # Start workload and end workload markers
        query = Query(0, 1, 999000)
        total_queries.insert(0, query)
        
        query = Query(0, 1, 999000)
        total_queries.append(query)
            
        # Write the query list to the output file
        self.write_queries(total_queries)
        
        # Return the query list
        return total_queries
            

'''
Plot the generated workload
'''
def plot_workload(workload):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    plt.xlabel('Time')
    plt.ylabel('Warehouses')
    
    xvalues = []
    yvalues = []
    
    x_offset = 0
    for i in workload: 
        xvalues.append(x_offset)
        yvalues.append(i.query)
        x_offset += i.offset
    
    ax.plot(xvalues, yvalues)
    plt.show()
    

# Query specification (probability and SLA for a query type)
query_specification = [(0.70, 250, 301040), (0.20, 500, 301040), (0.10, 750, 301040)]
wrapper = WorkloadWrapper('real_workload.txt', query_specification)
workload = wrapper.generate(False)
plot_workload(workload)
