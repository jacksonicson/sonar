
load_profile = function(profile_name)
{
  name = paste('SIS_', i, '_cpu', sep='')
  print(paste('loading: ', name))
  
  execute = paste('python ', getwd(), '/../../Times/src/radapt.py ', name, sep='')
  
  b = read.csv(pipe(execute))
  if(length(b) == 2)  
  {
    data_csv = c(data_csv, list(b[[2]]) )  
  } else {
    print(paste('skipping: ', name))
    print(b)
  }
    
  return(data_csv)
}



load_profiles = function(range)
{
  data_csv = list()
  
  print('Loading TSD from Times...')
  for(i in range) {
    name = paste('SIS_', i, '_cpu', sep='')
    
    print(paste('loading: ', name))
    
    execute = paste('python ', getwd(), '/../../Times/src/radapt.py ', name, sep='')
    print(execute)
    b = read.csv(pipe(execute))
    if(length(b) == 2)  
    {
      data_csv = c(data_csv, list(b[[2]]) )  
    } else {
      print(paste('skipping: ', name))
      print(b)
    }
    
  }
  
  return(data_csv)
}
