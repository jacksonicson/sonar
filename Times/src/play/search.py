from service import times_client

connection = times_client.connect()

result = connection.find('.*_modified')

r_out = ''
for i in result:
    i = i.replace('_modified', '')
    print i
    r_out += ', "' + i + '"'
    
r_out = 'c(' + r_out[2:] + ')'
print r_out


times_client.close()