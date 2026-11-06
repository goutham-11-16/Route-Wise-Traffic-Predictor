from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import numpy as np

X = np.array([
[5.1,3.5,1.4,0.2],
[4.9,3,1.4,0.2],
[4.7,3.2,1.3,0.2],
[4.6,3.1,1.5,0.2],
[5,3.6,1.4,0.2],
[7,3.2,4.7,1.4],
[6.4,3.2,4.5,1.5],
[6.9,3.1,4.9,1.5],
[5.5,2.3,4,1.3],
[6.5,2.8,4.6,1.5],
[6.3,3.3,6,2.5],
[5.8,2.7,5.1,1.9],
[7.1,3,5.9,2.1],
[6.3,2.9,5.6,1.8],
[6.5,3,5.8,2.2]
])

y = ["setosa","setosa","setosa","setosa","setosa",
     "versicolor","versicolor","versicolor","versicolor","versicolor",
     "virginica","virginica","virginica","virginica","virginica"]

model = DecisionTreeClassifier(criterion="entropy")

model.fit(X,y)

pred = model.predict(X)

accuracy = accuracy_score(y,pred)
precision = precision_score(y,pred,average='macro')
recall = recall_score(y,pred,average='macro')
f1 = f1_score(y,pred,average='macro')

print("Accuracy:",accuracy)
print("Precision:",precision)
print("Recall:",recall)
print("F1 Score:",f1)