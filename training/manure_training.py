import json
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder

# 1. Đọc dữ liệu từ 2 file JSON
with open("Json_Data.json", "r", encoding='utf-8') as f:
    sensor_data = json.load(f)

with open("Analysis_results_by_dataset.json", "r",encoding='utf-8') as f:
    labels_data = json.load(f)

# 2. Trích xuất features từ sensor_data và label từ labels_data
features = []
labels = []

for sensor, label in zip(sensor_data, labels_data):
    obj = sensor["object"]
    feature_row = [
        obj.get("N"),
        obj.get("P"),
        obj.get("K"),
        obj.get("EC"),
        obj.get("Humidity_of_soil"),
        obj.get("Temperature_of_soil")
    ]

    features.append(feature_row)
    labels.append(label.get("Bón phân"))

le = LabelEncoder()
y_encoded = le.fit_transform(labels)

# 3. Chuyển về DataFrame
df = pd.DataFrame(features, columns=["N", "P", "K", "EC", "Humidity", "Temperature"])
df["Label"] = labels

# 4. Train RandomForestClassifier
X = df.drop("Label", axis=1)
y = y_encoded

print(X)
print("--------------------------------")
print(y)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# 5. Đánh giá
y_pred = clf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)



# In kết quả
print("Dự đoán:", le.inverse_transform(y_pred[:5]))
print("Thực tế:", le.inverse_transform(y_test[:5]))
print(f"Accuracy: {accuracy:.2f}")

# # (Optional) Lưu mô hình nếu cần
# import joblib
# joblib.dump(clf, "predict_manure.pkl")
# joblib.dump(le, "label_encoder.pkl")

import shap
import matplotlib.pyplot as plt

# 1. Sử dụng SHAP explainer mới
explainer = shap.Explainer(clf, X_train)

# 2. Tính SHAP values cho tập test
shap_values = explainer(X_test)

# 3. In tên các lớp
class_names = le.classes_
print("Các lớp:", class_names)

# 4. Vẽ biểu đồ SHAP theo từng lớp (đa lớp)
for i, class_name in enumerate(class_names):
    print(f"\nBiểu đồ SHAP cho lớp: {class_name}")
    shap.plots.beeswarm(shap_values[:, :, i], max_display=10, show=False)
    plt.title(f"SHAP Summary Plot - Lớp: {class_name}")
    plt.tight_layout()
    plt.show()
