from workload import profiles

'''
Maps domains to profiles
'''

class Domain:
    def __init__(self, domain, profileId, rain_target=False):
        self.domain = domain
        self.profileId = profileId
        self.rain_target = rain_target

domain_profile_mapping = [
    Domain('target0', 0, True),
    Domain('target1', 1, True),
    Domain('target2', 2, True),
    Domain('target3', 3, True),
    Domain('target4', 4, True),
    Domain('target5', 5, True),
    Domain('target6', 6, True),
    Domain('target7', 7, True),
    Domain('target8', 8, True),
    Domain('target9', 9, True),
    Domain('target10', 10, True),
    Domain('target11', 11, True),
    Domain('target12', 12, True),
    Domain('target13', 13, True),
    Domain('target14', 14, True),
    Domain('target15', 15, True),
    Domain('target16', 16, True),
    Domain('target17', 17, True),
    ]


def user_profile_by_name(domain):
    for entry in domain_profile_mapping:
        if entry.domain == domain:
            profiles.get_current_user_profile(entry.profileId)
        
    print 'WARN: no profileId configured for domain %s, using profileId with index 0' % domain
    return profiles.selected[0]


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
    for entry in domain_profile_mapping:
        profile = profiles.byindex(entry.profileId).name
        print '%s --- load --> %s' % (profile, entry.domain)
    
  
def dump(logger):
    out = ''
    for entry in domain_profile_mapping:
        profile = profiles.byindex(entry.profileId).name
        out += '%s > %s; ' % (profile, entry.domain)
    logger.info("Mapping: %s" % out)
        
if __name__ == '__main__':
    print_mapping()
