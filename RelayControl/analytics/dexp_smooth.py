import math

def double_exponential_smoother(data, alpha=0.85, gamma=0.9):
    if len(data) < 2:
        return 0
    
    alpha = float(alpha)
    gamma = float(gamma)
                
    s_tb = float(data[0]) 
    # b_tb = float(data[-1] - data[0]) / float(len(data) - 1)
    b_tb = float(data[1] - data[0])
    
    errors = 0
    
    # print '%s \t\t - \t %s \t\t %s \t\t %s' % ('x_t', 's_t', 'b_t', 'f_t1')
    for t in xrange(1, len(data)):
        s_t = alpha * data[t] + (1.0 - alpha) * (s_tb + b_tb)
        b_t = gamma * (s_t - s_tb) + (1.0 - gamma) * (b_tb)
        f_t1 = s_t + b_t
        
        error = 0
        if len(data) > (t+1):
            error = math.pow(f_t1 - data[t+1], 2)
            errors += error
        
        s_tb = s_t
        b_tb = b_t
        
        # print '%f \t - \t %f \t %f \t %f \t %f' % (data[t], s_t, b_t, f_t1, error)
        
    # print 'RMSE: %f' % (errors / len(data))
    return f_t1
        

def main():
    data = (6.4, 5.6, 7.8, 8.8, 11, 11.6, 16.7, 15.3, 21.6, 22.4, 23.2, 20, 17, 14, 15, 5.6, 7.8, 8.8, 11, 11.6, 16.7, 15.3, 21.6, 22.4, 23.2, 20, 17, 14, 15, 16, 17.5, 19.5, 18.5, 21.5, 23, 24.5, 25, 25.3, 25.1, 25.2)
    print double_exponential_smoother(data)
    
    from service import times_client
    from workload import util
    con = times_client.connect()
    
    data = con.load('SIS_222_cpu_profile_trace')
    _ , demand = util.to_array(data)
    
    print double_exponential_smoother(demand)
    
    for i in xrange(0, len(demand) / 5):
        start = i*5
        end = (i+1) * 5
        double_exponential_smoother(demand[start : end])
    
    times_client.close()


if __name__ == '__main__':
    main() 
