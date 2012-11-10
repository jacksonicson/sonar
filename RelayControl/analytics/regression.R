data = read.csv('C:/temp/reg.csv')
print(data)
org.data = data

x=data$mix0.server
y=data$mix0.cpu
res = lm(x~y)
summary(res)
plot(x,y)


