data = read.csv('C:/temp/migration-data.csv', sep='\t')

diff = data$source.during - data$source.before
hist(diff)
length(diff)
diff = diff[is.finite(diff)]
mean(diff)
median(diff)

diff = data$target.during - data$target.before
diff = diff[is.finite(diff)]
hist(diff)
mean(diff)