import storage

def load_configuration(suite, traces):
    
    json_obj = {
                'suite_identifier' : suite,
                'custom.traces' : traces,
                }
    
    results = storage.targets.find(json_obj)
    for result in results:
        print result['custom']['lookahead']
        print result['results']
    
    
def load_failed_runs(suite):
    json_obj = {
                'suite_identifier' : suite,
                'status' : 'failed',
                }
    
    results = storage.targets.find(json_obj)
    for result in results:
        print result['exception']
        print result['exception']['stack_trace']
        print ''


def find_suites():
    json_obj = {
                }
    
    results = storage.suites.find(json_obj)
    for result in results:
        print result


def check_suite_status():
    json_obj = {}
    results = storage.suites.find(json_obj)
    for result in results:
        id = result['_id']
        
        json_obj = {
                    'run' : id
                    }
        run_targets = storage.targets.find(json_obj)
        
        total = 1
        succeeded = 0
        failed = 0
        new = 0
        for run_target in run_targets: 
            status = run_target['status']
            total += 1
            if status == 'new':
                new += 1
            elif status == 'succeeded':
                succeeded += 1
            elif status == 'failed':
                failed += 1
            
        succeeded_percentage = float(succeeded) * 100.0 / float(total)
            
        print 'summary for run %s' % (result['identifier'])
        print 'total %s, new %s, succeeded %s, failed %s' % (total, new, succeeded, failed)
        print 'finished %s' % (succeeded_percentage)
        print ''

def show_suite(suite):
    json_obj = {
                'suite' : suite,
                }
    
    results = storage.targets.find(json_obj)
    for result in results:
        for log in result['results']['logs']:
            print log
            print '##################'
    
  
def extract_dsapp_limited(suite):
    json_obj = {
                'suite' : suite,
                'loader' : 'de.tum.in.dss.target.dsapplus.DsappLaunchConfiguration',
                # 'status' : 'successful',
                }
    results = storage.targets.find(json_obj)
    
    x = []
    y = []
    
    
    file = open('dsapp_limited.csv', 'w')
    file.write('lookahead')
    file.write(',')
    file.write('timesteps')
    file.write(',')
    file.write('migration_overhead_in')
    file.write(',')
    file.write('migration_overhead_out')
    file.write(',')
    file.write('migration_count)')
    file.write(',')
    file.write('server_count')
    file.write(',')
    file.write('overall optimal')
    file.write(',')
    file.write('sequence')
    file.write(',')
    file.write('traces')
    file.write('\n')
    
    counter = 0
    average = 0
    for run_target in results:
        counter += 1
        print "result"
        custom = run_target['custom']
        
        # Check if the rseults are already available
        if 'results' not in run_target:
            print 'Missing results'
            continue 
        
        result = run_target['results']
        
        migration_overhead_in = custom['migration_overhead_incoming']
        migration_overhead_out = custom['migration_overhead_outgoing']
        lookahead = custom['lookahead']
        
        migration_count = result['migration_count']
        
        server_count = result['server_count']
        
        traces = ''
        for trace in custom['traces']:
            traces += trace + ' '
        
        
        optimal = True
        for status in result['model_status']:
            if status != 2:
                optimal = False
                break
        
        allocation = str(result['allocation_sequence'])
        allocation = allocation.replace(',', '|')
        print allocation
        
        file.write(str(custom['lookahead']))
        file.write(',')
        file.write(str(custom['timesteps']))
        file.write(',')
        file.write(str(migration_overhead_in))
        file.write(',')
        file.write(str(migration_overhead_out))
        file.write(',')
        file.write(str(migration_count))
        file.write(',')
        file.write(str(server_count))
        file.write(',')
        file.write(str(optimal))
        file.write(',')
        file.write(allocation)
        file.write(',')
        file.write(str(traces))
        file.write('\n')
        
        
        average += server_count
        x.append(counter)
        y.append(int(server_count))
        
        #print "lookahead %s mig out %s mig in %s      mig count %s server count %s" % (lookahead,
        #                                                                               migration_overhead_out, migration_overhead_in, migration_count, server_count)
        
        
    file.close()
    
    # average = float(average) / float(counter)
   
    #print average
    return x, y
  
    
def extract_dsapp_single(suite):
    json_obj = {
                'suite' : suite,
                'loader' : 'de.tum.in.dss.target.dsapplus.DsappLaunchConfigurationSingle',
                'status' : 'successful',
                }
    results = storage.targets.find(json_obj)
    
    x = []
    y = []
    
    
    file = open('dsapp.csv', 'w')
    file.write('lookahead')
    file.write(',')
    file.write('migration_overhead_in')
    file.write(',')
    file.write('migration_overhead_out')
    file.write(',')
    file.write('migration_count)')
    file.write(',')
    file.write('server_count')
    file.write(',')
    file.write('model_status')
    file.write(',')
    file.write('traces')
    file.write('\n')
    
    counter = 0
    average = 0
    for run_target in results:
        counter += 1
        print "result"
        custom = run_target['custom']
        result = run_target['results']
        
        migration_overhead_in = custom['migration_overhead_incoming']
        migration_overhead_out = custom['migration_overhead_outgoing']
        lookahead = custom['lookahead']
        
        migration_count = result['migration_count']
        
        server_count = result['server_count']
        
        traces = ''
        for trace in custom['traces']:
            traces += trace + ' '
        
        
        file.write(str(custom['lookahead']))
        file.write(',')
        file.write(str(migration_overhead_in))
        file.write(',')
        file.write(str(migration_overhead_out))
        file.write(',')
        file.write(str(migration_count))
        file.write(',')
        file.write(str(server_count))
        file.write(',')
        file.write(str(result['model_status']))
        file.write(',')
        file.write(str(traces))
        file.write('\n')
        
        average += server_count
        x.append(counter)
        y.append(int(server_count))
        
        #print "lookahead %s mig out %s mig in %s      mig count %s server count %s" % (lookahead,
        #                                                                               migration_overhead_out, migration_overhead_in, migration_count, server_count)
        
        
    file.close()
    
    average = float(average) / float(counter)
    print average
    return x, y


def extract_ssapv(suite):
    json_obj = {
                'suite' : suite,
                'loader' : 'de.tum.in.dss.target.ssapv.SsapvLaunchConfiguration',
                'status' : 'successful',
                }
    results = storage.targets.find(json_obj)
    
    x = []
    y = []
    
    
    file = open('ssapv.csv', 'w')
    file.write('timesteps')
    file.write(',')
    file.write('server_count')
    file.write(',')
    file.write('traces')
    file.write('\n')
    
    counter = 0
    average = 0
    for run_target in results:
        counter += 1
        print "result"
        custom = run_target['custom']
        result = run_target['results']
        
        server_count = result['server_count'] * custom['timesteps']
        
        traces = ''
        for trace in custom['traces']:
            traces += trace + ' '
            

        file.write(str(custom['timesteps']))
        file.write(',')
        file.write(str(server_count))
        file.write(',')
        file.write(str(traces))
        file.write('\n')
        
        average += server_count
        x.append(counter)
        y.append(int(server_count))
        
    file.close()
    
    average = float(average) / float(counter)
    print average
    return x, y

if __name__ == '__main__':
    #load_configuration()
    #load_failed_runs();
    # find_suites()
    # check_suite_status()
    # show_suite('configuration13')
    print "loading"
    suite = 'configuration1318506314'
    #extract_dsapp_single(suite)
    extract_dsapp_limited(suite)
    #extract_ssapv(suite)
