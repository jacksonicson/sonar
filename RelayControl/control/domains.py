from workload import profiles

'''
Maps domains to profiles
(domain, profile index, rain target)
'''
domain_profile_mapping = [
    ('glassfish0', 4, True),
    ('glassfish1', 10, True),
    ('glassfish2', 2, True),
    ('glassfish3', 4, True),
    ('glassfish4', 5, True),
    ('glassfish5', 6, True),
    ('mysql0', 4),
    ('mysql1', 10),
    ('mysql2', 2),
    ('mysql3', 3),
    ('mysql4', 4),
    ('mysql5', 5),
    ]

def print_mapping():
    for entry in domain_profile_mapping:
        profile = profiles.byindex(entry[1]).name
        print '%s --- load --> %s' % (profile, entry[0])
        
if __name__ == '__main__':
    print_mapping()
