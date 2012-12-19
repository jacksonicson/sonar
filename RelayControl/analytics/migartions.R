library('MASS')

########################################
## Duration ############################
########################################
data = read.csv('C:/temp/migration-times.csv', sep='\t')
times.elements = length(data$duration)
times.duration = mean(data$duration)
times.quantiles = quantile(data$duration)

y = data$duration
params = fitdistr(y, densfun="log-normal")

x = seq(0,100)
hist(y, main=NULL, xlab="Migration duration", ylab="Probability", prob=TRUE)
hx = dlnorm(x=x, meanlog=3.3, sdlog=0.27)
lines(x, hx, col='red', lwd=3)

cat('length:', times.elements, ' mean duration:', times.duration, ' quantiles:', times.quantiles)
print('Log normal distribution params:')
print(params)

########################################
## Migration Data ######################
########################################
data = read.csv('C:/temp/migration-data.csv', sep='\t')

# Migration duration
plot(data$duration, log(data$domain.cpu.before))

# Migration failures
mean(data$errors)
errors.none = length(data$errors[data$errors == 0])
errors.count = length(data$errors)
errors.per = errors.none / errors.count
print(errors.per)

quantile(data$errors, c(.95))




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
