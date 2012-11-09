data = read.csv('C:/temp/Experiments - ANOVA.csv')
print(data)
org.data = data
# number of factors (one factor in this case - CPU for this)
# factors are split into levels (RR, SSAPv and Sandpiper for this)
# deepen is the number of samples per level

# First look at the data
boxplot(data, ylab="CPU", xlab="Controller")


# Rearrange the data (2 column)
data = stack(data)
names(data) = c('cpu', 'controller')
print(data)

res = aov(cpu ~ controller, data=data)

# Can the null hyptothesis can be rejected (no change)
# Where are the difference

# Tukey HSD
tk = TukeyHSD(res)
# tk
plot(tk)
summary(res)

# Scheffe Test
# s <- scheffe.test(res,"cpu", group=FALSE)

# Run a Shapiro Wilk Normality Test on the data to see if it is normal distributed
# ANOVA needs normal distributed data and more importantly with similar variations
shapiro.test(org.data$Sandpiper)
qqnorm(org.data$Sandpiper)
# Check for equal variations
# homoscedascity 


