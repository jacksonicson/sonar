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


def continous_single_exponential_smoothed(f_t, data_t, alpha):
    # Smoothing equation (1)
    # f_t is the forecasted value for f_{t+1}
    f_t = alpha * data_t + (1 - alpha) * f_t
    return f_t

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
        f_t = continous_single_exponential_smoothed(f_t, data[t], alpha)
        
        # Ad value to smoothed TS
        smoothed.append(f_t)
        
        # Update errors
        if (t + 1) < len(data):
            error = math.pow(f_t - data[t + 1], 2)
            errors += error
       
    # Update RMSE error
    errors = (errors / len(data))
    
    # Return forecast, smoothened TS and the RMSE error
    return f_t, smoothed, errors


def continuouse_double_exponential_smoothed(c_t, T_t, data_t, alpha=0.2, beta=0.1):
    # Backup current c_t
    c_tp = c_t
    
    # Equation (1) for c_t
    c_t = alpha * data_t + (1.0 - alpha) * (c_t + T_t)
    
    # Equation (2) for T_t
    T_t = beta * (c_t - c_tp) + (1.0 - beta) * (T_t)
    
    # Forecast next value
    f_t = c_t + T_t
    return f_t, c_t, T_t


def double_exponential_smoother(data, periods=1,alpha=0.2, beta=0.1):
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
        f_t, c_t, T_t = continuouse_double_exponential_smoothed(c_t, T_t, data[t], alpha, beta)
        smoothed.append(f_t)
        
        # Error calculation
        if (t + 1) < len(data):
            error = math.pow(f_t - data[t + 1], 2)
            errors += error

    # Forecast for the next periods
    f_t = c_t + periods * T_t
        
    # Update RMSE error
    errors = (errors / len(data))
    
    # Return forecast, smoothened TS and the RMSE error
    return f_t, smoothed, errors
        

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
    _, s0, _ = single_exponential_smoother(demand)
    _, s1, _ = double_exponential_smoother(demand)
    
    # Plot original data with forecasted
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(demand)
    ax.plot(s0)
    ax.plot(s1)
    plt.show()


if __name__ == '__main__':
    main() 
