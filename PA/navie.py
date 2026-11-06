from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import numpy as np

X = np.array([
[242,11.52,4.02,23.2,25.4,30],
[290,12.48,4.3056,24,26.3,31.2],
[40,4.1472,2.268,12.9,14.1,16.2],
[69,5.2983,2.8217,16.5,18.2,20.3],
[270,8.3804,4.2476,23.6,26,28.7],
[270,8.1454,4.2485,24.1,26.5,29.3],
[55,6.8475,2.3265,13.5,14.7,16.5],
[60,6.5772,2.3142,14.3,15.5,17.4],
[5.9,2.112,1.408,7.5,8.4,8.8],
[32,3.528,1.9992,12.5,13.7,14.7],
[1600,9.6,6.144,56,60,64],
[1550,9.6,6.144,56,60,64],
[6.7,1.7388,1.0476,9.3,9.8,10.8],
[7.5,1.972,1.16,10,10.5,11.6]
])

y = ["Bream","Bream","Roach","Roach","Whitefish","Whitefish",
     "Parkki","Parkki","Perch","Perch","Pike","Pike","Smelt","Smelt"]

model = GaussianNB()

model.fit(X,y)

pred = model.predict(X)

accuracy = accuracy_score(y,pred)
precision = precision_score(y,pred,average='macro')
recall = recall_score(y,pred,average='macro')
f1 = f1_score(y,pred,average='macro')

print(accuracy,precision,recall,f1)