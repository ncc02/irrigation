import json
from datetime import datetime
import pytz
from pymongo import MongoClient
from config import MONGODB_URI

class SoilSensorData:
    def __init__(self):
        self.application_id = "9507fa5e-26f5-4ec9-9815-cdba90c51c0e"
        self.device_eui = "ac1f09fffe052a03"
        self.topic = f"application/{self.application_id}/device/{self.device_eui}/event/up"
        # Kết nối MongoDB
        self.client = MongoClient(MONGODB_URI)
        self.db = self.client['irrigation']
        self.collection = self.db['soil_sensor_raw']
        
    def parse_sensor_data(self, message):
        try:
            data = json.loads(message)
            # Kiểm tra fPort
            if data.get('fPort') != 1:
                return None
                
            # Lưu dữ liệu thô vào MongoDB
            data['timestamp'] = datetime.now(pytz.UTC)
            self.collection.insert_one(data)
            print(f"Đã lưu dữ liệu thô vào MongoDB: {data}")
            
            # Lấy thông tin thiết bị
            device_info = data.get('deviceInfo', {})
            sensor_data = data.get('object', {})
            
            # Tạo bản tin đã xử lý
            processed_data = {
                'timestamp': data.get('time'),
                'device_name': device_info.get('deviceName'),
                'device_eui': device_info.get('devEui'),
                'sensor_data': {
                    'phosphorus': sensor_data.get('P'),  # P (Phosphorus)
                    'electrical_conductivity': sensor_data.get('EC'),  # EC (Electrical Conductivity)
                    'soil_humidity': sensor_data.get('Humidity_of_soil'),  # Độ ẩm đất
                    'nitrogen': sensor_data.get('N'),  # N (Nitrogen)
                    'battery': sensor_data.get('Battery_percent'),  # Pin
                    'potassium': sensor_data.get('K'),  # K (Potassium)
                    'soil_temperature': sensor_data.get('Temperature_of_soil')  # Nhiệt độ đất
                }
            }
            
            return processed_data
            
        except Exception as e:
            print(f"Lỗi khi xử lý dữ liệu cảm biến: {e}")
            return None
            
    def format_sensor_data(self, data):
        if not data:
            return "Không có dữ liệu"
            
        sensor_data = data['sensor_data']
        return f"""
Thông tin cảm biến đất:
- Thời gian: {data['timestamp']}
- Tên thiết bị: {data['device_name']}
- ID thiết bị: {data['device_eui']}
- Dữ liệu cảm biến:
  + Nhiệt độ đất: {sensor_data['soil_temperature']}°C
  + Độ ẩm đất: {sensor_data['soil_humidity']}%
  + Độ dẫn điện (EC): {sensor_data['electrical_conductivity']} mS/cm
  + Nito (N): {sensor_data['nitrogen']} mg/kg
  + Photpho (P): {sensor_data['phosphorus']} mg/kg
  + Kali (K): {sensor_data['potassium']} mg/kg
  + Pin: {sensor_data['battery']}%
""" 