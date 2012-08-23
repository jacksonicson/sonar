import convolution
from service import times_client
from times import ttypes

selected = [('O2_business_UPDATEDSSLINE', 60 * 60), # Burst in the evening
            ('O2_business_ADDUCP', 60 * 60), # Day workload
            ('O2_business_LINECONFIRM', 60 * 60), # Day and night workload
            ('O2_retail_ADDORDER', 60 * 60), # Night and low day workload
            ('O2_retail_SENDMSG', 60 * 60), # Day workload flattens till evening
            ('O2_retail_PORTORDER', 60 * 60), # Random spikes 
            ('O2_retail_UPDATEDSS', 60 * 60), # Night workload
            ('SIS_221_cpu', 5 * 60), # Evening workload 
            ('SIS_194_cpu', 5 * 60), # Average day high evening workload 
            ('SIS_375_cpu', 5 * 60), # Trend to full CPU utilization starting in the morning
            ('SIS_213_cpu', 5 * 60), # High dynamic range 
            ('SIS_211_cpu', 5 * 60), # High dynamic range
            ('SIS_83_cpu', 5 * 60), # Highly volatile varying levels 
            ('SIS_394_cpu', 5 * 60), # Multiple peaks
            ('SIS_381_cpu', 5 * 60), # High volatile 
            ('SIS_383_cpu', 5 * 60), # Bursts and then slow
            ('SIS_415_cpu', 5 * 60), # Volatility bursts  
            ('SIS_198_cpu', 5 * 60), # Random
            ('SIS_269_cpu', 5 * 60), # Random
            ]
    

mix0 =      [('O2_business_UPDATEDSSLINE', 60 * 60), # Burst in the evening
            ('O2_business_ADDUCP', 60 * 60), # Day workload
            ('O2_business_LINECONFIRM', 60 * 60), # Day and night workload
            ('O2_retail_ADDORDER', 60 * 60), # Night and low day workload
            ('O2_retail_SENDMSG', 60 * 60), # Day workload flattens till evening
            ('O2_retail_PORTORDER', 60 * 60), # Random spikes 
            ('O2_retail_UPDATEDSS', 60 * 60), # Night workload
            ('SIS_221_cpu', 5 * 60), # Evening workload 
            ('SIS_194_cpu', 5 * 60), # Average day high evening workload 
            ('SIS_375_cpu', 5 * 60), # Trend to full CPU utilization starting in the morning
            ('SIS_213_cpu', 5 * 60), # High dynamic range 
            ('SIS_211_cpu', 5 * 60), # High dynamic range
            ('SIS_83_cpu', 5 * 60), # Highly volatile varying levels 
            ('SIS_394_cpu', 5 * 60), # Multiple peaks
            ('SIS_381_cpu', 5 * 60), # High volatile 
            ('SIS_383_cpu', 5 * 60), # Bursts and then slow
            ('SIS_415_cpu', 5 * 60), # Volatility bursts  
            ('SIS_198_cpu', 5 * 60), # Random
            ('SIS_269_cpu', 5 * 60), # Random
            ]


def store_profile(times_connection, name, profile, frequency):
    name = name + '_profile'
    print 'storing profile with name %s' % (name)
    times_connection.create(name, frequency)
    
    elements = []
    for i in range(0, len(profile)):
        item = profile[i]
        
        element = ttypes.Element()
        element.timestamp = i * 60
        element.value = item 
        elements.append(element)

    times_connection.append(name, elements)

def build_and_save(mix):
    connection = times_client.connect()

    for ts in mix:
        print 'processing %s' % (ts[0])
        profile, frequency = convolution.process_trace(connection, ts)
        store_profile(connection, ts[0], profile, frequency)
        
    times_client.close()
    
if __name__ == '__main__':
    # Build profiles and save them
    build_and_save(mix0)