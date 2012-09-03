from workload import profiles

'''
Maps domains to profiles
'''

class Map:
    def __init__(self, domain, profile, rain_target=False):
        self.domain = domain
        self.profile = profile
        self.rain_target = rain_target

domain_profile_mapping = [
    Map('target0', 0, True),
    Map('target1', 1, True),
    Map('target2', 2, True),
    Map('target3', 3, True),
    Map('target4', 4, True),
    Map('target5', 5, True),
    
    Map('target6', 6, True),
    Map('target7', 7, True),
    Map('target8', 8, True),
    
    Map('target9', 9, True),
    Map('target10', 10, True),
    Map('target11', 11, True),
    Map('target12', 12, True),
    Map('target13', 13, True),
    Map('target14', 14, True),
    
    Map('target15', 15, True),
    Map('target16', 16, True),
    Map('target17', 17, True),
    ]


def profile_by_name(domain):
    for entry in domain_profile_mapping:
        if entry.domain == domain:
            if len(profiles.selected) > entry.profile:
                return profiles.selected[entry.profile].name
        
    print 'Warn: no profile configured for domain %s, using profile with index 0' % domain
    return profiles.selected[0]


def print_mapping():
    for entry in domain_profile_mapping:
        profile = profiles.byindex(entry.profile).name
        print '%s --- load --> %s' % (profile, entry.domain)
    
        
if __name__ == '__main__':
    print_mapping()
