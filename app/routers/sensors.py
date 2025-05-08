from fastapi import APIRouter, HTTPException
from typing import List
import json
from pathlib import Path
import os
from app.models.models import SensorRecord

router = APIRouter()

@router.get("/sensors", response_model=List[SensorRecord])
async def get_sensor_data():
    try:
        # Lấy đường dẫn tuyệt đối đến thư mục gốc của dự án
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Đường dẫn đến file JSON
        json_path = os.path.join(base_dir, "training", "Json_Data.json")
        
        # Đọc và parse file JSON
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
        # Chuyển đổi dữ liệu thành list các SensorRecord
        sensor_records = [SensorRecord(**record) for record in data]
        
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
        # Lấy đường dẫn tuyệt đối đến thư mục gốc của dự án
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Đường dẫn đến file JSON
        json_path = os.path.join(base_dir, "training", "Json_Data.json")
        
        # Đọc và parse file JSON
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
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