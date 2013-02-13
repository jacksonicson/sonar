import analytics
import configuration
import csv
import matplotlib.pyplot as plt
import scipy.stats as stats
import numpy as np

def __read_table(name):
    indexmap = {}
    table = []
    header = False
    with open(configuration.path(name,'csv'), 'rb') as db_file:
        dbreader = csv.reader(db_file, delimiter='\t')

        for row in dbreader:
            if header == False:
                for i, name in enumerate(row):
                    print name
                    indexmap[name] = i 
                header = True
                continue
            table.append(row)
            
    return indexmap, table

def __hist_migration_time():
    indexmap, table = __read_table('migration-times')
    times = []
    for row in table:
        time = float(row[indexmap['duration']])
        times.append(time)
        
        
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.hist(times, bins=20, color='white')
    ax.set_ylabel('Frequency')
    ax.set_xlabel('Migration duration')
    
    rv = stats.lognorm(3.317601554, 0.271082797 )
         
    x = np.linspace(0, 100)
    ax.plot(x, rv.pdf(x)*5500)
    
    plt.show()

def __hist_migration_cpu_effect():
    indexmap, table = __read_table('migration-data') 
            
    deltas_source = []
    deltas_target = []
    for row in table:
        source_before = float(row[indexmap['source-before']])
        source_during = float(row[indexmap['source-during']])
        deltas_source.append(source_during - source_before)
        
        target_before = float(row[indexmap['target-before']])
        target_during = float(row[indexmap['target-during']])
        deltas_target.append(target_during - target_before)
            
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.hist(deltas_source, bins=10, color='white')
    ax.set_ylabel('Frequency')
    ax.set_xlabel('CPU change before/during migration')
    fig.savefig(configuration.path('migration_source','pdf'))
    fig.show()
        
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.hist(deltas_target, bins=10, color='white')
    ax.set_ylabel('Frequency')
    ax.set_xlabel('CPU change before/during migration')
    fig.savefig(configuration.path('migration_target','pdf'))
    fig.show()
            

def main():
    __hist_migration_cpu_effect()
    # __hist_migration_time()

if __name__ == '__main__':
    main()