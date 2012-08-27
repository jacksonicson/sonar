
def __fetch_start_benchamrk_syncs(connection, host, frame):
    pass

def __fetch_rain_data(connection, hosts, frame):
    pass


def __fetch_controller_data(connection, host, frame):
    pass

def __fetch_srv_data(connection, hosts, sensors, frame):
    pass

def __to_timestamp(date):
    return 0


def main():
    # start and stop timestamp
    start = __to_timestamp('27.08.2012 8:00')
    stop = __to_timestamp('27.08.2012 8:00')
    frame = (start, stop)
    
    connection = None
    
    # Synchronize benchmark
    syncs = __fetch_start_benchamrk_syncs(connection, 'Andreas-PC', frame)
    frame = syncs
    
    # Load rain data    
    rain = __fetch_rain_data(connection, ('load0', 'load1'), frame)
    
    # Load controller data
    control = __fetch_controller_data(connection, ('Andreas-PC'), frame)
    
    # Load srv* data
    srvs = [ 'srv%i' % i for i in range(0, 6)]
    cpu = __fetch_srv_data(connection, srvs, 'psutilcpu', frame)
    
    

if __name__ == '__main__':
    main()