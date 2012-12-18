# Times
data = read.csv('C:/temp/migration-times.csv', sep='\t')
length(data$duration)
mean(data$duration)
quantile(data$duration)
hist(data$duration)

library('MASS')
y = data$duration
params = fitdistr(y, densfun="log-normal")
print(params)
x = seq(0,100)
hist(y, main=NULL, ylab=NULL, xlab=NULL)
hx = dlnorm(x=x, meanlog=3.3, sdlog=0.27)
lines(x, hx*5500, col='red')

# CPU Overload
data = read.csv('C:/temp/migration-data.csv', sep='\t')
diff = data$source.during - data$source.before
hist(diff)
length(diff)
diff = diff[is.finite(diff)]
source.mean = mean(diff)
source.median = median(diff)
cat("Migration source: ", "mean =", source.mean, "median =", source.median)

diff = data$target.during - data$target.before
diff = diff[is.finite(diff)]
hist(diff)
target.mean = mean(diff)
target.median = median(diff)
cat("Migration source: ", "mean =", target.mean , "median =", target.median)