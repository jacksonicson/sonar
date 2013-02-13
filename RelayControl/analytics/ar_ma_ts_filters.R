source('times.import.R')

library(forecast)

# Load TSD
data = c("O2_retail_ADDLINEORDER") #, "SIS_350_cpu_profile_norm", "SIS_240_cpu_profile_user", "SIS_211_cpu_profile_norm", "SIS_198_cpu_profile_norm", "SIS_199_cpu_profile_user", "SIS_211_cpu_profile_norm", "SIS_345_cpu_profile_norm", "O2_business_ADDLINEORDER_profile_norm", "SIS_253_cpu_profile_norm", "SIS_314_cpu_profile_user", "SIS_385_cpu_profile_user", "SIS_375_cpu_profile_norm", "O2_business_UPDATEDSSLINE_profile_norm", "SIS_222_cpu_profile_user", "SIS_213_cpu_profile_user", "SIS_225_cpu_profile_norm", "O2_retail_UPDATEACCOUNT_profile_user", "SIS_313_cpu_profile_norm", "O2_retail_ADDORDER_profile_norm", "O2_retail_ADDUCP_profile_user", "SIS_305_cpu_profile_user", "SIS_383_cpu_profile_norm", "SIS_279_cpu_profile_user", "SIS_397_cpu_profile_norm", "SIS_207_cpu_profile_norm", "SIS_269_cpu_profile_norm", "O2_retail_PORTORDER_profile_user", "O2_retail_SENDMSG_profile_norm", "SIS_225_cpu_profile_user", "SIS_178_cpu_profile_user", "SIS_172_cpu_profile_user", "O2_business_UPDATEDSS_profile_user", "O2_business_SENDMSG_profile_norm", "SIS_340_cpu_profile_user", "SIS_222_cpu_profile_norm", "SIS_394_cpu_profile_user", "O2_retail_UPDATEACCOUNT_profile_norm", "SIS_271_cpu_profile_user", "SIS_340_cpu_profile_norm", "SIS_163_cpu_profile_norm", "SIS_271_cpu_profile_norm", "SIS_345_cpu_profile_norm", "O2_business_CONTRACTEXT_profile_user", "O2_retail_ADDUCP_profile_norm", "SIS_314_cpu_profile_norm", "SIS_415_cpu_profile_norm", "SIS_83_cpu_profile_norm", "SIS_394_cpu_profile_norm", "SIS_397_cpu_profile_user", "O2_business_UPDATEDSSLINE_profile_user", "SIS_211_cpu_profile_user", "SIS_375_cpu_profile_user", "SIS_221_cpu_profile_norm", "SIS_308_cpu_profile_user", "SIS_350_cpu_profile_user", "SIS_374_cpu_profile_user", "O2_retail_ADDORDER_profile_user", "SIS_179_cpu_profile_user", "SIS_387_cpu_profile_norm", "SIS_298_cpu_profile_norm", "O2_business_ADDUCP_profile_user", "O2_business_LINECONFIRM_profile_norm", "SIS_344_cpu_profile_norm", "SIS_194_cpu_profile_norm", "SIS_344_cpu_profile_user", "O2_retail_SENDMSG_profile_user", "O2_business_ADDUCP_profile_norm", "SIS_175_cpu_profile_user", "SIS_381_cpu_profile_norm", "SIS_345_cpu_profile_user", "SIS_308_cpu_profile_norm", "O2_business_ADDORDER_profile_norm", "O2_retail_UPDATEDSS_profile_norm", "SIS_309_cpu_profile_user", "O2_retail_ADDLINEORDER_profile_norm", "SIS_264_cpu_profile_user", "O2_retail_CONTRACTEXT_profile_user", "SIS_198_cpu_profile_user", "SIS_387_cpu_profile_user", "SIS_83_cpu_profile_user", "SIS_393_cpu_profile_norm", "SIS_234_cpu_profile_norm", "SIS_189_cpu_profile_norm", "SIS_292_cpu_profile_norm", "SIS_161_cpu_profile_user", "SIS_198_cpu_profile_norm", "SIS_29_cpu_profile_user", "SIS_162_cpu_profile_user", "SIS_207_cpu_profile_user", "O2_retail_UPDLINEORDER_profile_norm", "SIS_178_cpu_profile_norm", "SIS_292_cpu_profile_user", "O2_retail_PORTORDER_profile_norm", "SIS_350_cpu_profile_user", "SIS_279_cpu_profile_norm", "SIS_189_cpu_profile_user", "SIS_163_cpu_profile_user", "SIS_213_cpu_profile_norm", "SIS_298_cpu_profile_user", "O2_retail_UPDATEDSS_profile_user", "SIS_172_cpu_profile_norm", "SIS_310_cpu_profile_norm", "SIS_264_cpu_profile_norm", "O2_retail_CONTRACTEXT_profile_norm", "SIS_245_cpu_profile_norm", "SIS_374_cpu_profile_norm", "SIS_310_cpu_profile_user", "SIS_345_cpu_profile_user", "SIS_209_cpu_profile_user", "SIS_161_cpu_profile_norm", "SIS_275_cpu_profile_user", "SIS_175_cpu_profile_norm", "O2_retail_UPDLINEORDER_profile_user", "SIS_383_cpu_profile_user", "SIS_275_cpu_profile_norm", "SIS_216_cpu_profile_norm", "SIS_216_cpu_profile_user", "SIS_198_cpu_profile_user", "O2_business_LINECONFIRM_profile_user", "SIS_350_cpu_profile_norm", "SIS_245_cpu_profile_user", "O2_business_ADDORDER_profile_user", "SIS_393_cpu_profile_user", "O2_business_UPDATEACCOUNT_profile_norm", "O2_business_ADDLINEORDER_profile_user", "SIS_188_cpu_profile_norm", "SIS_179_cpu_profile_norm", "SIS_177_cpu_profile_norm", "SIS_415_cpu_profile_user", "SIS_253_cpu_profile_user", "SIS_29_cpu_profile_norm", "SIS_381_cpu_profile_user", "SIS_209_cpu_profile_norm", "SIS_309_cpu_profile_norm", "O2_business_SENDMSG_profile_user", "SIS_269_cpu_profile_user", "SIS_194_cpu_profile_user", "SIS_221_cpu_profile_user", "SIS_188_cpu_profile_user", "SIS_305_cpu_profile_norm", "SIS_240_cpu_profile_norm", "SIS_211_cpu_profile_user", "SIS_177_cpu_profile_user", "SIS_234_cpu_profile_user", "O2_business_UPDATEDSS_profile_norm", "SIS_313_cpu_profile_user", "SIS_162_cpu_profile_norm", "SIS_385_cpu_profile_norm", "O2_business_CONTRACTEXT_profile_norm", "SIS_211_cpu_profile_user", "O2_business_UPDATEACCOUNT_profile_user", "SIS_211_cpu_profile_norm", "SIS_199_cpu_profile_norm")

results = list()
for(element in data)
{
  print(element)
  name = element
  
  result_nom = load_profile(name)
  y = result_nom
  # ts.mean = meanf(y, 100) 
  # ts.snavie = snaive(y, 100)
  
  # Ar model forecast
  fc = ar(y)
  fc = forecast(fc, h=100)
  plot(fc, xlim=c(1800,2000))
    
  # Holt's winter forecast
  fc = holt(y, 100)
  print(fc)
  #plot(fc, xlim=c(800, 2000))
  #print(fc$mean)
  
  # Simple exponential forecast
  fc = ses(y, 100)
  plot(fc, xlim=c(1800, 1900))
  
  # Holt-Winters' additive method
  #fc = hw(y, h=100)
  #plot(fc, xlim=c(800, 2000))
  
  
}

