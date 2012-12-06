d = read.csv('C:/temp/migrations.csv', sep='\t', header=FALSE)

mean((d$V1))
sd((d$V1))
     
quantile(d$V1)

min(d$V1)
max(d$V1)

library('MASS')
y = d$V1
params = fitdistr(y, densfun="log-normal")
# par(mar=c(1,1,1,1))
x = seq(0,100)
hist(y, main=NULL, ylab=NULL, xlab=NULL)
hx = dlnorm(x=x, meanlog=3.3, sdlog=0.27)
lines(x, hx*5500, col='red')