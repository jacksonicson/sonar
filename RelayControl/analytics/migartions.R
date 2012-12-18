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

# Data
data = read.csv('C:/temp/migration-data.csv', sep='\t')

# Migration failures
mean(data$errors)
errors.none = length(data$errors[data$errors == 0])
errors.count = length(data$errors)
errors.per = errors.none / errors.count
print(errors.per)

errors.data = data[data$errors > 0,]
print(errors.data)
plot(errors.data$source.during, errors.data$errors)
plot(errors.data$target.during, errors.data$errors)

summary(lm(errors.data$target.during ~ errors.data$errors))


errors.data$source.during
errors.data$target.during



# NET Overhead ######################
diff = (data$source.net.during - data$source.net.before) / 1024
hist(diff)
source.mean = mean(diff)
source.median = median(diff)
cat("Migration source NET: ", "mean =", source.mean, "median =", source.median)

diff = (data$target.net.during - data$target.net.before) / 1024
hist(diff)
source.mean = mean(diff)
source.median = median(diff)
cat("Migration source NET: ", "mean =", source.mean, "median =", source.median)



# CPU Overhead ######################
diff = data$source.during - data$source.before
hist(diff)
length(diff)
diff = diff[is.finite(diff)]
source.mean = mean(diff)
source.median = median(diff)
cat("Migration source: ", "mean =", source.mean, "median =", source.median)

diff = (data$target.during - data$target.before) 
diff = diff[is.finite(diff)]
hist(diff)
target.mean = mean(diff)
target.median = median(diff)
cat("Migration source: ", "mean =", target.mean , "median =", target.median)
