import math
import matplotlib.pyplot as plt
import numpy as np
import statsmodels as sm2
    
def ar_forecast(data, smoothing=False):
    if smoothing:
        # Smoothen data
        data = double_exponential_smoother(data)[1]
    
    try:
        model = sm2.tsa.ar_model.AR(data).fit()
        value = model.predict(len(data), len(data) + 20)
        return value[-1]
    except:
        return data[-1]


class Status(object):
    def __init__(self):
        self.f_agile = None
        self.f_stable = None
        self.b_bar = None
        self.mw = [10]
        self.x_prev = None
        self.x_bar = None
        
        self.ucl = None
        self.lcl = None
        
        self.forecast = 0

def continous_flip_flop(x, status=None):
    '''
    Implementation of the flip flop filter as described by Minkyong Kim and Brian Noble
    EWMA = Exponential Weighted Moving Average
    buffer = Status information that was returned by the previous call 
    '''
    
    # Initialize status
    if status == None:
        status = Status()
    
    # Update agile and stable EWMA
    status.f_agile = continous_single_exponential_smoothed(status.f_agile, x, 0.9)
    status.f_stable = continous_single_exponential_smoothed(status.f_stable, x, 0.1)
    
    # Update estimated population mean \bar{x}
    status.x_bar = continous_single_exponential_smoothed(status.x_bar, x, 0.7)
    
    # Calculate \bar{MW}
    mw_average = np.mean(status.mw)
        
    # Update upper and lower control limits
    ucl = status.x_bar + 3 * (mw_average / 1.128)
    lcl = status.x_bar - 3 * (mw_average / 1.128)
    status.ucl = ucl
    status.lcl = lcl
    
    # print 'agile %f lower %f upper %f' % (status.f_agile, lcl, ucl)
    
    # Run flip-flop logic
    # if status.f_agile >= lcl and status.f_agile <= ucl:
    if status.forecast >= lcl and status.forecast <= ucl:
        forecast = status.forecast
        
        # Update moving range
        if status.x_prev != None:
            delta = abs(x - status.x_prev)
            status.mw.append(delta)
            l = 30
            if len(status.mw) > l:
                status.mw = status.mw[-l:]
                
    else:
        print 'stable'
        forecast = status.f_stable
    
    # Return status and forecast
    status.x_prev = x
    status.forecast = forecast 
    return forecast, status


def continous_single_exponential_smoothed(f_t, data_t, alpha):
    # Smoothing equation (1)
    # f_t is the forecasted value for f_{t+1}
    
    if f_t == None: 
        return data_t
    
    f_t = alpha * data_t + (1 - alpha) * f_t
    
    return f_t


def single_exponential_smoother(data, alpha=0.3):
    if len(data) < 2:
        return 50  # Neutral CPU value
    
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


def double_exponential_smoother(data, periods=1, alpha=0.2, beta=0.3):
    if len(data) < 2:
        return 50  # neutral cpu value
    
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
    random = np.random.normal(loc=0, scale=2, size=len(demand))
    demand += random

    # Run smoother
    s0 = []
    s1 = []
    ua = []
    ul = []
    status = None
    f_t = None
    for x in demand:
        forecast, status = continous_flip_flop(x, status)
        s0.append(forecast)
        
        ua.append(status.ucl)
        ul.append(status.lcl)
        
        f_t = continous_single_exponential_smoothed(f_t, x, 0.1)
        s1.append(f_t)
        
    
    # Plot original data with forecasted
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    ax.plot(demand)
    ax.plot(s0, lw=2)
    #ax.plot(ua)
    #ax.plot(ul)
    ax.fill_between(xrange(0, len(ua)), ua, ul, interpolate=True, facecolor='lightgray', lw=0)
    # ax.plot(s1)
    plt.show()


if __name__ == '__main__':
    main() 
