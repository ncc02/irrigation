from pydantic import BaseModel
from typing import Dict, Optional

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

# Model cho Device Info
class DeviceInfo(BaseModel):
    tenantId: str
    tenantName: str
    applicationId: str
    applicationName: str
    deviceProfileId: str
    deviceProfileName: str
    deviceName: str
    devEui: str
    deviceClassEnabled: str
    tags: Dict

# Model cho Sensor Record
class SensorRecord(BaseModel):
    deduplicationId: str
    time: str
    deviceInfo: DeviceInfo
    devAddr: str
    adr: bool
    dr: int
    fCnt: int
    fPort: int
    confirmed: bool
    data: str
    object: SensorData 