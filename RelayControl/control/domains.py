from workload import profiles
import random

'''
Maps domains to profiles
'''

class Domain:
    def __init__(self, domain, profileId, rain_target=False):
        self.domain = domain
        self.profileId = profileId
        self.rain_target = rain_target

domain_profile_mapping = []

def recreate():
    global domain_profile_mapping
    domain_profile_mapping = []
    for i in xrange(360):
        offset = 90
        target_index = offset + i
        target_index = random.randint(0, 400)
        domain_profile_mapping.append(Domain('target%i' % i, target_index, True))
        
recreate()

###############################################################################
###############################################################################

def cpu_profile_by_name(domain):
    for entry in domain_profile_mapping:
        if entry.domain == domain:
            return profiles.get_current_cpu_profile(entry.profileId)
        
    print 'WARN: no profileId configured for domain %s, using profileId with index 0' % domain
    return profiles.get_current_cpu_profile(0)

def user_profile_by_name(domain):
    for entry in domain_profile_mapping:
        if entry.domain == domain:
            return profiles.get_current_user_profile(entry.profileId)
        
    print 'WARN: no profileId configured for domain %s, using profileId with index 0' % domain
    return profiles.get_current_user_profile(0)


def has_domain(name):
    for mapping in domain_profile_mapping:
        if mapping.domain == name:
            return True
        
    return False 

def index_of(name):
    index = 0
    for mapping in domain_profile_mapping:
        if mapping.domain == name:
            return index
        index += 1
        
    return None


def print_mapping():
    print 'Dumping domain profile mappings...'
    for entry in domain_profile_mapping:
        profile = profiles.get_current_user_profile(entry.profileId)
        print '%s --- load --> %s' % (profile, entry.domain)
    print 'End dumping domain profile mappings.'
    
  
def dump(logger):
    out = ''
    for entry in domain_profile_mapping:
        profile = profiles.get_current_user_profile(entry.profileId)
        out += '%s > %s; ' % (profile, entry.domain)
    logger.info("Mapping: %s" % out)
        
        
if __name__ == '__main__':
    print_mapping()
