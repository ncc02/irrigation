from fastapi import APIRouter, HTTPException, Query, Response
from typing import List, Dict
import json
from pathlib import Path
import os
from app.models.models import SensorRecord
from math import ceil
from functools import lru_cache
from datetime import datetime, timedelta

router = APIRouter()

# Cache cho dữ liệu JSON
@lru_cache(maxsize=1)
def get_cached_sensor_data() -> List[Dict]:
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    json_path = os.path.join(base_dir, "training", "Json_Data.json")
    
    with open(json_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# Hàm helper để tính toán phân trang
def calculate_pagination(data: List, page: int, page_size: int) -> tuple:
    total_records = len(data)
    total_pages = ceil(total_records / page_size)
    
    if page > total_pages and total_pages > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Trang yêu cầu ({page}) vượt quá tổng số trang ({total_pages})"
        )
    
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    return total_records, total_pages, start_idx, end_idx

@router.get("/sensors", response_model=List[SensorRecord])
async def get_sensor_data(
    response: Response,
    page: int = Query(1, ge=1, description="Số trang"),
    page_size: int = Query(10, ge=1, le=100, description="Số phần tử trên mỗi trang"),
    device_name: str = Query(None, description="Lọc theo tên thiết bị"),
    start_time: datetime = Query(None, description="Thời gian bắt đầu (ISO format)"),
    end_time: datetime = Query(None, description="Thời gian kết thúc (ISO format)")
):
    try:
        # Lấy dữ liệu từ cache
        data = get_cached_sensor_data()
        
        # Lọc dữ liệu theo các điều kiện
        filtered_data = data
        if device_name:
            filtered_data = [record for record in filtered_data 
                           if record["deviceInfo"]["deviceName"] == device_name]
        
        if start_time:
            filtered_data = [record for record in filtered_data 
                           if datetime.fromisoformat(record["time"].replace("Z", "+00:00")) >= start_time]
        
        if end_time:
            filtered_data = [record for record in filtered_data 
                           if datetime.fromisoformat(record["time"].replace("Z", "+00:00")) <= end_time]
        
        # Tính toán phân trang
        total_records, total_pages, start_idx, end_idx = calculate_pagination(
            filtered_data, page, page_size
        )
        
        # Lấy dữ liệu cho trang hiện tại
        paginated_data = filtered_data[start_idx:end_idx]
        
        # Chuyển đổi sang SensorRecord
        sensor_records = [SensorRecord(**record) for record in paginated_data]
        
        # Thêm thông tin phân trang vào header
        response.headers["X-Total-Records"] = str(total_records)
        response.headers["X-Total-Pages"] = str(total_pages)
        response.headers["X-Current-Page"] = str(page)
        response.headers["X-Page-Size"] = str(page_size)
        
        return sensor_records
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Không tìm thấy file dữ liệu")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Lỗi khi đọc file JSON")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sensors/{deduplication_id}", response_model=SensorRecord)
async def get_sensor_by_id(deduplication_id: str):
    try:
        # Lấy dữ liệu từ cache
        data = get_cached_sensor_data()
        
        # Tìm bản ghi theo deduplicationId
        for record in data:
            if record["deduplicationId"] == deduplication_id:
                return SensorRecord(**record)
                
        # Nếu không tìm thấy
        raise HTTPException(status_code=404, detail=f"Không tìm thấy bản ghi với ID: {deduplication_id}")
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Không tìm thấy file dữ liệu")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Lỗi khi đọc file JSON")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 