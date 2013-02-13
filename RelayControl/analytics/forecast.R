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