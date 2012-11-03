source('times.import.R')

# Load TSD
if(exists('data_csv') == FALSE)
{
  data_csv = load_profiles(1:70)
  list.ts = list()
  for(element in data_csv) {
    l = ts(element, frequency=1)  
    list.ts = c(list.ts, list(l))
  }
}

main = function()
{
  lags = c()
  for(i in 1:2)
    lags = c(lags, period_detect(i))
  
  hist(lags)
}

mean_hist = function()
{
  means = c()
  for(element in list.ts) {
    m = mean(element)
    means = c(means, m)
  }
  hist(means)
}

period_detect = function(index)
{
  # Set of lambdas
  lambdas = c()
  
  # ACF filtering
  acf.data = acf(list.ts[[index]], lag.max=1000)
  threshold = max(acf.data$acf) / 2
  found = acf.data$lag[acf.data$acf > threshold]
  lambdas = c(lambdas, found)
  
  # Periodogram filtering
  pdg = periodogram(list.ts[[index]])
  threshold = max(pdg$spec) / 2
  found = pdg$freq[pdg$spec > threshold] * length(list.ts[[index]])
  lambdas = c(lambdas, found)
    
  # Filter lambdas
  lambdas.old = lambdas
  lambdas = c()
  interval = 5
  multiples = c(1, 2,3,4,5, 6, 12, 24, 7*24) * 60
  for(lambda in lambdas.old)
  {
    if(lambda < 10)
      next
    
    lambda = lambda * interval
    nearest = abs(multiples - lambda)
    nearest_neighbour = which(nearest == min(nearest))
    
    lambda = multiples[nearest_neighbour] / interval
    lambdas = c(lambdas, lambda)
  }
  
  # Remove all dulicates
  lambdas = unique(lambdas)
  
  # Print number of found lambdas
  print(paste('lambdas found: ', length(lambdas)))
  print(lambdas)
        
  # Seach best lambda by ACF
  acf.data = acf(list.ts[[index]], lag.max=20000)
  lambda.values = c()
  for(lambda in lambdas)
  {
    multi = 1:20
    checkpoints = multi * lambda
    lambda.value = mean(acf.data$acf[checkpoints])
    if(!is.na(lambda.value))
      lambda.values = c(lambda.values, lambda.value)
    else
      lambda.values = c(lambda.values, 0)
  }
  
  i.best.value = which(lambda.values == max(lambda.values))
  final.lambda = lambdas[i.best.value]
  print(paste('best lag: ', final.lambda))
  
  return(final.lambda)
}

# Main function
main()