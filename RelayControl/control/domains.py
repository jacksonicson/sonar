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


def profile_by_name(domain):
    for entry in domain_profile_mapping:
        if entry.domain == domain:
            if len(profiles.selected) > entry.profileId:
                return profiles.selected[entry.profileId].name
        
    print 'Warn: no profileId configured for domain %s, using profileId with index 0' % domain
    return profiles.selected[0]


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
