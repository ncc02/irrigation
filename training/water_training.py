import json
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

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
    # Chuyển nhãn "Có" thành 1, "Không" thành 0
    label_val = 1 if label.get("Tưới nước") == "Có" else 0
    features.append(feature_row)
    labels.append(label_val)

# 3. Chuyển về DataFrame
df = pd.DataFrame(features, columns=["N", "P", "K", "EC", "Humidity", "Temperature"])
df["Label"] = labels

# 4. Train RandomForestClassifier
X = df.drop("Label", axis=1)
y = df["Label"]

print(X)
print("--------------------------------")
print(y)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# 5. Đánh giá
y_pred = clf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(y_pred[:5])
print(y_test[:5])
print(f"Accuracy: {accuracy:.2f}")


import json
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import shap
import matplotlib.pyplot as plt

# 1. Nạp và tiền xử lý dữ liệu như trước
# (bỏ qua phần này để tập trung vào SHAP)

# 2. Huấn luyện mô hình
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# 3. Tạo explainer và tính SHAP values
explainer = shap.TreeExplainer(clf)              # TreeExplainer trả về 3D array cho binary :contentReference[oaicite:3]{index=3}
shap_values = explainer.shap_values(X_test)      # shap_values.shape == (n_test, n_feat, 2)

# 4. Chọn lớp “1” (tưới nước = Có)
shap_vals_class1 = shap_values[:, :, 1]          # cắt lấy ma trận 2D :contentReference[oaicite:4]{index=4}

# 5. Vẽ beeswarm summary plot
shap.summary_plot(shap_vals_class1, X_test)      # đúng chuẩn 2D input :contentReference[oaicite:5]{index=5}
plt.tight_layout()
plt.show()

