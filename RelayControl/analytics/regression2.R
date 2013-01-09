data = read.csv('C:/temp/regression.csv', sep='\t')
print(data)

# Filter 
print(data[data$Mix=='MIX1',])

names(data)
hist(data$RTim)
hist(data$Migrations)
hist(data$Servers)

plot(data$Controller, data$Migrations)

glm(data$RTim ~ data$Migrations + data$Servers)

ff = factor(data$Controller)
glm(ff ~ (data$Migrations))
lm(data$Migrations ~ (ff))
ft = as.numeric(data$Controller)
lim = glm(as.numeric(data$Controller) ~ data$Migrations + as.numeric(data$Mix) + data$RTime)
print(lim)

r = residuals(lim)
hist(r)

lm1 = lm(data$RTime ~ data$Controller + data$Mix + data$Servers)
length(data)
summary(lm1)
hist(residuals(lm1))

summary(lm(data$Server ~ data$Mix + data$Controller))

summary(lm(data$RTime ~ data$Controller + data$Mix + data$Servers))
summary(lm(data$RTime ~ data$Controller + data$Mix + data$Servers+ data$MaxRTime + data$Migrations))
summary(lm(data$MaxRTime ~ data$Migrations + data$Mix + data$Servers))


summary(lm(data$RTime ~ data$Servers + data$Violations))
summary(lm(data$Violations ~ data$Servers + data$RTime + data$Controller))
summary(lm(data$Servers ~ data$Mix + data$Controller))
           
           
lm2 = lm(data$MaxRTime ~ data$Controller + data$Mix)

hist(residuals(lm2))


coefficients(lm2)
confint(lm2, level=0.95)
fitted(lm2)
residuals(lm2)
anova(lm2)
influence(lm2)


layout(matrix(c(1,2,3,4),1,1))
plot(lm2)


