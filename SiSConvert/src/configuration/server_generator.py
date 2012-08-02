import storage
 
def write_server(identifier, costs, capacity):
    
    json_obj = {
                'identifier' : identifier,
                'costs' : costs,
                'capacity' : capacity,
                }
        
    storage.servers.save(json_obj)


if __name__ == '__main__':
    #write_server('paper1_500', 42, 500)
    #write_server('paper1_200', 42, 200)
    # write_server('paper1_100', 42, 100)
    #write_server('paper1_50', 42, 50)
    #write_server('paper1_150', 42, 150)
    #write_server('paper1_400', 42, 400)
    # write_server('paper1_2', 42, 2)
    write_server('paper1_1', 42, 1)
