from fastapi import APIRouter, Depends
from app.models.models import IrrigationRequest, IrrigationResponse
from app.predict.irrigation import IrrigationPredictor
from functools import lru_cache

router = APIRouter()

@lru_cache()
def get_predictor():
    return IrrigationPredictor()

@router.post("/irrigation", response_model=IrrigationResponse)
async def predict_irrigation(
    request: IrrigationRequest,
    predictor: IrrigationPredictor = Depends(get_predictor)
):
    # Dự đoán tất cả thông tin
    should_water, water_volume, manure_type = await predictor.predict(request.sensor_data)
    
    # Tạo message tổng hợp
    message = "Tưới vì độ ẩm thấp và thiếu dinh dưỡng" if should_water else "Không cần tưới nước"
    if should_water:
        message += f". Cần tưới với lượng {water_volume} lít/cây"
    if manure_type != "Không xác định":
        message += f". Loại phân bón phù hợp: {manure_type}"
    
    return IrrigationResponse(
        device_name=request.device_name,
        should_water=should_water,
        water_volume=water_volume,
        manure_type=manure_type,
        message=message
    ) 