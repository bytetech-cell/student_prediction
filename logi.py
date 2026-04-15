import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Load data
train = pd.read_excel("training_data.xlsx")
test = pd.read_excel("testing_data.xlsx")

# 🔧 Drop useless column
train = train.drop("student_id", axis=1)
test = test.drop("student_id", axis=1)

# 🔧 Encode categorical column
le = LabelEncoder()

train["extracurricular_participation"] = le.fit_transform(train["extracurricular_participation"])
test["extracurricular_participation"] = le.transform(test["extracurricular_participation"])

train["result"] = le.fit_transform(train["result"])
test["result"] = le.transform(test["result"])

# 🎯 Features & Target
X = train.drop("result", axis=1)
y = train["result"]

# Split (optional but good practice)
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# 🤖 Model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Validation accuracy
y_pred = model.predict(X_val)
print("Validation Accuracy:", accuracy_score(y_val, y_pred))

# 🔮 Test prediction
X_test = test.drop("result", axis=1)
y_test = test["result"]

y_test_pred = model.predict(X_test)
print("Test Accuracy:", accuracy_score(y_test, y_test_pred))





