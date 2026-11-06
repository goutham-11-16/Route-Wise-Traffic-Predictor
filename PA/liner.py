import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.metrics import mean_squared_log_error

experience = np.array([1.1,1.3,1.5,2,2.2,2.9,3,3.2,3.2,3.7]).reshape(-1,1)
salary = np.array([39343,46205,37731,43525,39891,56642,60150,54445,64445,57189])

model = LinearRegression()
model.fit(experience, salary)

pred = model.predict(experience)

SSE = np.sum((salary - pred)**2)
MSSE = SSE/len(salary)
MAE = mean_absolute_error(salary,pred)
RMSE = np.sqrt(mean_squared_error(salary,pred))
RMSLE = np.sqrt(mean_squared_log_error(salary,pred))
R2 = r2_score(salary,pred)

print("SSE:",SSE)
print("MSSE:",MSSE)
print("MAE:",MAE)
print("RMSE:",RMSE)
print("RMSLE:",RMSLE)
print("R2:",R2)