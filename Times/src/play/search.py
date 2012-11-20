from service import times_client

connection = times_client.connect()

result = connection.find('.*')

for i in result:
    print i

times_client.close()