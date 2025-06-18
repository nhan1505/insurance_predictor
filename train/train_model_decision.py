import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import LabelEncoder
import pickle

# 1. Đọc dữ liệu
data = pd.read_csv('insurance.csv')

# 2. Tiền xử lý
data['sex'] = LabelEncoder().fit_transform(data['sex'])         # Nam:1, Nữ:0
data['smoker'] = LabelEncoder().fit_transform(data['smoker'])   # Có:1, Không:0
data['region'] = data['region'].map({'northeast':0, 'northwest':1, 'southeast':2, 'southwest':3})

# 3. Tạo feature và label
X = data[['age', 'sex', 'bmi', 'smoker', 'region']]
y = data['charges']

# 4. Chia tập train/test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 5. Thiết lập GridSearchCV để tìm tham số tốt nhất cho Decision Tree
param_grid = {
    'max_depth': [None, 10, 20, 30],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

model = DecisionTreeRegressor(random_state=42)
grid_search = GridSearchCV(estimator=model, param_grid=param_grid, cv=5, n_jobs=-1, verbose=2)
grid_search.fit(X_train, y_train)

# 6. In ra tham số tốt nhất
print("Best Parameters:", grid_search.best_params_)

# 7. Kiểm tra độ chính xác của mô hình với tham số tốt nhất
best_model = grid_search.best_estimator_
score = best_model.score(X_test, y_test)
print(f'Accuracy: {score*100:.2f}%')

# 8. Lưu model tốt nhất
pickle.dump(best_model, open('model_decision.pkl', 'wb'))
print("✅ Best model saved as model_decision.pkl")
