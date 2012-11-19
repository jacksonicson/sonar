
def domain_to_server_cpu(target, domain, domain_cpu):
        domain_cpu_factor = target.cpu_cores / domain.cpu_cores
        return domain_cpu / domain_cpu_factor

