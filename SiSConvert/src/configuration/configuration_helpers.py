import random
import storage
import time
import update

def create_suite(suite_identifier, text='', labels=[]):
    """
    Checks if a suite with suite_identifier already exists. If this is not the 
    case, a new suite document is created and its identifier returned. 
    """
    
    # Check if the suite already exists
    query = {
             'identifier' : suite_identifier,
             }
    suite = storage.suites.find_one(query)
    if suite is not None:
        print 'suite %s already exists' % (suite_identifier)
        return None
        
    json_obj = {
                'identifier' : suite_identifier,
                'text' : text,
                'labels' : labels,
                }
    
    print 'suite created: %s' % (suite_identifier)
    
    return storage.suites.save(json_obj)


def create_target(suite, suite_id, depends, loader_class, priority=0):
    """
    Creates the base configuration for a target. This does not contain any 
    specific configuration settings for the target implementation.         
    """
    
    json_obj = {
                'suite' : suite,
                'suite_id' : suite_id,
                'depends_upon' : depends,
                'depends_resolved' : [],
                'priority' : priority,
                
                'status' : 'new',
                'loader' : loader_class,
                
                'mail' : 'andreas.wolke@in.tum.de',
                }
    return json_obj
    
    
def add_custom_base(target_configuration, traces=None, servers=None):
    """
    Add custom fields which are used by all targets. 
    """
    
    # Get the custom element
    custom = target_configuration['custom']
    
    custom['gurobi_threads'] = 7
    custom['TIME_LIMIT'] = long(45 * 60)
    custom['server_size_modulation'] = False
    
    if traces is not None:
        custom['traces'] = traces
        
    if servers is not None:
        custom['servers'] = servers
        
#    custom['traces_postprocessor'] = {
#                                      'class' : 'de.tum.in.dss.service.AggregationPostprocessor',
#                                      'aggregation_time' : 120.0,
#                                      }


############################################
# Configurations
############################################

def write_configuration_dsap(suite, identifier, suite_id, timesteps, traces, servers, depends=[], priority=0):
    json_obj = create_target(suite, suite_id, identifier, depends, 'de.tum.in.dss.target.dsap.DsapLaunchConfiguration', priority)
    json_obj['custom'] = {
                        'timesteps' : timesteps, # Timesteps for the simulate
                        }                
    add_custom_base(json_obj, traces, servers)
    
    return storage.targets.save(json_obj)


def write_configuration_dsap_limit(suite, identifier, suite_id, timesteps, traces, servers, depends=[], max_migrations=2, priority=0):
    json_obj = create_target(suite, suite_id, identifier, depends,
                                         'de.tum.in.dss.target.dsapr.DsaprLaunchConfiguration', priority)
    json_obj['custom'] = {
                        'timesteps' : timesteps, # Timesteps to simulate
                        'max_migrations' : max_migrations,
                        }
    add_custom_base(json_obj, traces, servers)                
    
    return storage.targets.save(json_obj)


def write_configuration_ssap(suite, identifier, suite_id, traces, servers, depends=[], priority=0):
    json_obj = create_target(suite, suite_id, identifier, depends, 'de.tum.in.dss.ssap.SsapLaunchConfiguration', priority)
    json_obj['custom'] = {
                          }
    add_custom_base(json_obj, traces, servers)
    
    return storage.targets.save(json_obj)


def write_configuration_ssapv(suite, identifier, suite_id, timesteps, traces, servers, depends=[], priority=0):
    json_obj = create_target(suite, suite_id, identifier, depends, 'de.tum.in.dss.target.ssapv.SsapvLaunchConfiguration', priority)
    json_obj['custom'] = {
                          'timesteps' : timesteps, # Timesteps to simulate
                          }
    add_custom_base(json_obj, traces, servers)
    
    return storage.targets.save(json_obj)
 
 
def write_configuration_dsapp_single(suite, identifier, suite_id, timesteps, lookahead, traces, servers, alloc, overhead_out, overhead_in, depends=[], priority=0):
    json_obj = create_target(suite, suite_id, identifier, depends, 'de.tum.in.dss.target.dsapplus.DsappLaunchConfigurationSingle', priority)
    json_obj['custom'] = {
                            'timesteps' : timesteps, # Timesteps to simulate
                            'lookahead' : lookahead, # Use a lookahead
                            'initial_allocation' : alloc, # Initial service/server allocation
                            'migration_overhead_outgoing' : overhead_out,
                            'migration_overhead_incoming' : overhead_in,
                          }
    add_custom_base(json_obj, traces, servers)
    
    return storage.targets.save(json_obj)


def write_configuration_dsapps(suite, suite_id, timesteps, lookahead, traces, servers, alloc, overhead_out, overhead_in, depends=[], priority=0):
    json_obj = create_target(suite, suite_id, depends, 'de.tum.in.dss.target.dsaps.DsapsLaunchConfiguration', priority)
    json_obj['custom'] = {
                            'timesteps' : timesteps, # Timesteps to simulate
                            'lookahead' : lookahead, # Use a lookahead
                            'initial_allocation' : alloc, # Initial service/server allocation
                            'migration_overhead_outgoing' : overhead_out,
                            'migration_overhead_incoming' : overhead_in,
                          }
    add_custom_base(json_obj, traces, servers)
    
    return storage.targets.save(json_obj)


def write_configuration_dsapp(suite, suite_id, timesteps, lookahead, traces, servers, alloc, overhead_out, overhead_in, depends=[], priority=0):
    json_obj = create_target(suite, suite_id, depends, 'de.tum.in.dss.target.dsapplus.DsappLaunchConfiguration', priority)
    json_obj['custom'] = {
                            'timesteps' : timesteps, # Timesteps to simulate
                            'lookahead' : lookahead, # Use a lookahead
                            'initial_allocation' : alloc, # Initial service/server allocation
                            'migration_overhead_outgoing' : overhead_out,
                            'migration_overhead_incoming' : overhead_in,
                          }
    add_custom_base(json_obj, traces, servers)
    
    return storage.targets.save(json_obj)


def write_allocation_transfer(suite, identifier, suite_id, source_target_id, allocation_identifier, depends=[], priority=0):
    json_obj = create_target(suite, suite_id, identifier, depends, 'de.tum.in.dss.target.transfer.TransferLaunchConfiguration', priority)
    json_obj['custom'] = {
                            'source_target_id' : source_target_id,
                            'allocation_identifier' : allocation_identifier
                          }
    add_custom_base(json_obj)
    return storage.targets.save(json_obj)

