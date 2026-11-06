from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import numpy as np

height=[174,189,185,195,149,189,147,154,174,169,195,159,192,155,191,153,157,140,144]
weight=[96,87,110,104,61,104,92,111,90,103,81,80,101,51,79,107,110,129,145]

X=np.column_stack((height,weight))

gender=['Male','Male','Female','Female','Male','Male','Male','Male','Male',
        'Female','Male','Female','Female','Male','Male','Female','Female','Male','Male']

model=KNeighborsClassifier(n_neighbors=3)

model.fit(X,gender)

pred=model.predict(X)

accuracy=accuracy_score(gender,pred)
precision=precision_score(gender,pred,pos_label="Male",average='binary')
recall=recall_score(gender,pred,pos_label="Male")
f1=f1_score(gender,pred,pos_label="Male")

print("Accuracy:",accuracy)
print("Precision:",precision)
print("Recall:",recall)
print("F1 Score:",f1)