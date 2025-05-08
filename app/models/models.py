from pydantic import BaseModel

# Model cho dữ liệu cảm biến
class SensorData(BaseModel):
    P: float
    EC: float
    Humidity_of_soil: float
    N: float
    Battery_percent: float
    K: float
    Temperature_of_soil: float

# Model cho request và response tưới nước
class IrrigationRequest(BaseModel):
    device_name: str
    sensor_data: SensorData

class IrrigationResponse(BaseModel):
    device_name: str
    should_water: bool
    water_volume: str
    manure_type: str
    message: str 