import matplotlib.pyplot as plt
from service import times_client

def allocate_domains(name):
    print 'Downloading...'
    connection = times_client.connect()
    
    timeSeries = connection.load(name)
    print 'done'
    
    times_client.close()
    print 'complete'
    
    # Generate (x,y) signal
    signal = []
    for element in timeSeries.elements:
        signal.append(element.value)
    
    # Setup the new plot
    fig = plt.figure()
    fig.set_size_inches((10, 10))
    plt.xlabel('Time')
    plt.ylabel('Load')
    
    # Create a new subplot
    ax = fig.add_subplot(1, 1, 1)
    ax.set_title('TimeSeries %s' % (name));
    ax.plot(range(0, len(signal)), signal)   

    # Display the plot        
    plt.show()
                

if __name__ == '__main__':
    allocate_domains('SIS_161_cpu_profile_norm')
