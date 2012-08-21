from statsmodels.tsa.arima_model import ARMA
test = [1,2,3,2,4,3,4,3,6,4,5,3,4,3,4,2,3,4,2,23,1,23,4]
testv=test
test = ARMA(test)


fit = test.fit((2,2), disp=False)

print 'prediction'
print test.predict(fit.params, start=len(testv)-1, end=100)