hosts_map = {}
hosts = []


def add_host(hostname, function):
    if function not in hosts_map:
        hosts_map[function] = []
        
    hosts_map[function].append(hostname)
    hosts.append(hostname)


def get_index(host):
    return hosts.index(host)


def get_hosts(function):
    hostnames = hosts_map[function]
    result = []
    for host in hostnames:
        index = get_index(host)
        result.append((index, host))
        
    return result


def get_hosts_list():
    return hosts
