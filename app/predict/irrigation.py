import joblib
import pandas as pd
from app.models.models import SensorData

class IrrigationPredictor:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(IrrigationPredictor, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.manure_model = joblib.load("app\predict\model_manure.pkl")
            self.label_encoder = joblib.load("app\predict\label_encoder_manure.pkl")
            self.water_model = joblib.load("app\predict\model_water.pkl")
            self._initialized = True
    
    async def predict(self, sensor_data: SensorData) -> tuple[bool, str, str]:
        # Lấy tất cả dữ liệu từ sensor một lần
        N = sensor_data.N
        P = sensor_data.P
        K = sensor_data.K
        EC = sensor_data.EC
        humidity = sensor_data.Humidity_of_soil
        temperature = sensor_data.Temperature_of_soil
        
        # 1. Kiểm tra điều kiện tưới nước từ model
        features = [[N, P, K, EC, humidity, temperature]]
        df = pd.DataFrame(features, columns=["N", "P", "K", "EC", "Humidity", "Temperature"])
        should_water = self.water_model.predict(df)[0] == 1
        
        # 2. Xác định lượng nước tưới
        if should_water:
            if 50 <= N <= 70 and 20 <= P <= 30 and 60 <= K <= 80:
                volume = "20-30"
            elif 80 <= N <= 100 and 30 <= P <= 40 and 100 <= K <= 120:
                volume = "30-40"
            elif 60 <= N <= 80 and 20 <= P <= 30 and 80 <= K <= 100:
                volume = "20-30"
            else:
                volume = "20-30"  # Mặc định tưới 20-30 lít
        else:
            volume = "0"
        
        # 3. Dự đoán loại phân bón
        prediction = self.manure_model.predict(features)[0]
        manure_type = self.label_encoder.inverse_transform([prediction])[0]
        
        return should_water, volume, manure_type 