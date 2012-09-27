from sonarlytics import to_timestamp, fetch_timeseries, fetch_logs

# Parameters
START = '16/09/2012 20:20:41'
END = '17/09/2012 03:30:41'
frame = (to_timestamp(START), to_timestamp(END))

# Fetch time series
data, time = fetch_timeseries('srv0', 'psutilcpu', frame)

# Fetch application logs
logs = fetch_logs('load0', 'rain', frame)

# Print 
for log in logs:
    print log

# Plotting
import matplotlib.pyplot as plt 
fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(time, data)
plt.show()