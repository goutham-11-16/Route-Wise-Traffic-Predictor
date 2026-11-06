import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.metrics import mean_squared_log_error, r2_score

age = [25,30,47,32,43,51,28,33,37,39,29,47]
exp = [1,3,2,5,10,7,5,4,5,8,1,9]
income = [30450,35670,31580,40130,47830,41630,41340,37650,40250,45150,27840,46110]

X = np.column_stack((age,exp))
y = income

model = LinearRegression()
model.fit(X,y)

pred = model.predict(X)

SSE = np.sum((y-pred)**2)
MSSE = SSE/len(y)
MAE = mean_absolute_error(y,pred)
RMSE = np.sqrt(mean_squared_error(y,pred))
RMSLE = np.sqrt(mean_squared_log_error(y,pred))
R2 = r2_score(y,pred)

print(SSE,MSSE,MAE,RMSE,RMSLE,R2)