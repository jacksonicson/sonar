import math
import matplotlib.pyplot as plt
import numpy as np
import statsmodels as sm2
import statsmodels.api as sm
    
def ar_forecast(data, smoothing=False):
    if smoothing:
        # Smoothen data
        data = double_exponential_smoother(data)[1]
    
    try:
        model = sm2.tsa.ar_model.AR(data).fit()
        value = model.predict(len(data), len(data) + 10)
        return value[-1]
    except:
        return data[-1]


def single_exponential_smoother(data, alpha=0.3):
    if len(data) < 2:
        return 50 # Neutral CPU value
    
    # Parameters and initial values
    # y_t0 has to be initialized
    alpha = float(alpha)
    f_t = float(data[0])
    
    # Sum of squared errors (RMSE)    
    errors = 0
    
    # Smoothed TS
    smoothed = [f_t]
    
    # Takes y_t and f_t and calculates f_{t+1} 
    for t in xrange(0, len(data)):
        # Smoothing equation (1)
        # f_t is the forecasted value for f_{t+1}
        f_t = alpha * data[t] + (1 - alpha) * f_t
        
        # Ad value to smoothed TS
        smoothed.append(f_t)
        
        # Update errors
        if (t + 1) < len(data):
            error = math.pow(f_t - data[t + 1], 2)
            errors += error
       
    # Update RMSE error
    errors = (errors / len(data))
    
    # Return last forecast 
    return f_t, smoothed
    

def double_exponential_smoother(data, periods=1,alpha=0.1, beta=0.08):
    if len(data) < 2:
        return 50 # neutral cpu value
    
    # Parameters and initial values
    alpha = float(alpha)
    beta = float(beta)
    
    # Initialize c and T values
    c_t = float(data[0]) 
    T_t = float(data[1] - data[0])
    f_t = c_t + T_t
    
    # root mean square errors (RMSE)
    errors = 0
    
    # Smoothed TS with the initial value
    smoothed = [f_t]
    
    # Run forecasting
    for t in xrange(0, len(data)):
        # Backup current c_t
        c_tp = c_t
        
        # Equation (1) for c_t
        c_t = alpha * data[t] + (1.0 - alpha) * (c_t + T_t)
        
        # Equation (2) for T_t
        T_t = beta * (c_t - c_tp) + (1.0 - beta) * (T_t)
        
        # Forecast next value
        f_t = c_t + T_t
        smoothed.append(f_t)
        
        # Error calculation
        if (t + 1) < len(data):
            error = math.pow(f_t - data[t + 1], 2)
            errors += error

    # Forecast for the next periods
    f_t = c_t + periods * T_t
        
    # Update RMSE error
    errors = (errors / len(data))
    
    # Return last forecast and the smoothened TS
    return f_t, smoothed
        

def main():
    from service import times_client
    from workload import util
    
    con = times_client.connect()
    data = con.load('SIS_222_cpu_profile_trace')
    _ , demand = util.to_array(data)
    times_client.close()
    
    random = np.random.lognormal(mean=0.0, sigma=1.5, size=len(demand))
    demand += random

    # Run smoother
    _, data = double_exponential_smoother(demand)
    
    # Plot original data with forecasted
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(demand)
    ax.plot(data)
    plt.show()


if __name__ == '__main__':
    main() 
