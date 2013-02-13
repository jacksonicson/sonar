data = read.csv('C:/temp/Experiments - ANOVA.csv')
print(data)
org.data = data

t.test(data$RR, data$Sandpiper)