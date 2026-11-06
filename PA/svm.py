from sklearn import svm
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import pandas as pd

data = {
'Outlook':['Rainy','Rainy','Overcast','Sunny','Sunny','Sunny','Overcast','Rainy','Rainy','Sunny','Rainy','Overcast','Overcast','Sunny'],
'Temperature':['Hot','Hot','Hot','Mild','Cool','Cool','Cool','Mild','Cool','Mild','Mild','Mild','Hot','Mild'],
'Humidity':['High','High','High','High','Normal','Normal','Normal','High','Normal','Normal','Normal','High','Normal','High'],
'Windy':['FALSE','TRUE','FALSE','FALSE','FALSE','TRUE','TRUE','FALSE','FALSE','FALSE','TRUE','TRUE','FALSE','TRUE'],
'Play':['No','No','Yes','Yes','Yes','No','Yes','No','Yes','Yes','Yes','Yes','Yes','No']
}

df = pd.DataFrame(data)

le = LabelEncoder()

for column in df.columns:
    df[column] = le.fit_transform(df[column])

X = df.drop('Play',axis=1)
y = df['Play']

model = svm.SVC()

model.fit(X,y)

pred = model.predict(X)

accuracy = accuracy_score(y,pred)
precision = precision_score(y,pred)
recall = recall_score(y,pred)
f1 = f1_score(y,pred)

print(accuracy,precision,recall,f1)