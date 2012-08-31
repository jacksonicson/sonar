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
    Map('target0', 4, True),
    Map('target1', 4, True),
    Map('target2', 4, True),
    Map('target3', 4, True),
    Map('target4', 4, True),
    Map('target5', 4, True),
    Map('target6', 4, True),
    Map('target7', 4, True),
    Map('target8', 4, True),
    Map('target9', 4, True),
    Map('target10', 4, True),
    Map('target11', 4, True),
    Map('target12', 4, True),
    Map('target13', 4, True),
    Map('target14', 4, True),
    Map('target15', 4, True),
    Map('target16', 4, True),
    Map('target17', 4, True),
    Map('target18', 4, True),
    
#    Map('glassfish0', 4, True),
#    Map('glassfish1', 10, True),
#    Map('glassfish2', 2, True),
#    Map('glassfish3', 4, True),
#    Map('glassfish4', 5, True),
#    Map('glassfish5', 6, True),
#    Map('mysql0', 4),
#    Map('mysql1', 10),
#    Map('mysql2', 2),
#    Map('mysql3', 3),
#    Map('mysql4', 4),
#    Map('mysql5', 5),
    ]


def profile_by_name(domain):
    for entry in domain_profile_mapping:
        if entry.domain == domain:
            return profiles.selected[entry.profile].name
        
    print 'Warn: no profile configured for domain %s, using profile with index 0' % domain
    return profiles.selected[0]


def print_mapping():
    for entry in domain_profile_mapping:
        profile = profiles.byindex(entry.profile).name
        print '%s --- load --> %s' % (profile, entry.domain)
    
        
if __name__ == '__main__':
    print_mapping()
