'''
Manages a list of hosts with types. This data structure is required to
trigger actions by the host type in the control scripts. 
'''

hosts_map = {}
hosts = []

def add_host(hostname, drone_type):
    if drone_type not in hosts_map:
        hosts_map[drone_type] = []
        
    hosts_map[drone_type].append(hostname)
    
    if hostname not in hosts:
        hosts.append(hostname)


def get_index(host):
    index = hosts.index(host)
    return index

def get_hosts(drone_type):
    if not hosts_map.has_key(drone_type):
        return []
    
    hostnames = hosts_map[drone_type]
    result = []
    for host in hostnames:
        result.append(host)
        
    return result


def get_hosts_list():
    return hosts
