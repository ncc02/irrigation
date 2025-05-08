import json
import joblib
import pandas as pd

# Dữ liệu mới
new_data = [
    {
        "object": {
            "P": 25.5,
            "EC": 1.29,
            "Humidity_of_soil": 59.5,
            "N": 45.3,
            "Battery_percent": 97.8,
            "K": 61.6,
            "Temperature_of_soil": 26.4
        }
    },
    {
        "object": {
            "P": 33.1,
            "EC": 1.23,
            "Humidity_of_soil": 54.0,
            "N": 30.4,
            "Battery_percent": 87.0,
            "K": 41.5,
            "Temperature_of_soil": 24.3
        }
    },
    {
        "object": {
            "P": 34.0,
            "EC": 0.9,
            "Humidity_of_soil": 54.3,
            "N": 23.5,
            "Battery_percent": 94.3,
            "K": 66.1,
            "Temperature_of_soil": 26.8
        }
    }
]

# Load mô hình
clf = joblib.load("predict_water.pkl")

# Chuẩn bị dữ liệu đầu vào
features = []
for item in new_data:
    obj = item["object"]
    feature_row = [
        obj.get("N"),
        obj.get("P"),
        obj.get("K"),
        obj.get("EC"),
        obj.get("Humidity_of_soil"),
        obj.get("Temperature_of_soil")
    ]
    features.append(feature_row)

# Chuyển thành DataFrame để dự đoán
df_new = pd.DataFrame(features, columns=["N", "P", "K", "EC", "Humidity", "Temperature"])
predictions = clf.predict(df_new)

# In kết quả
for i, pred in enumerate(predictions):
    print(f"Mẫu {i+1}: {'Tưới nước' if pred == 1 else 'Không tưới'}")
