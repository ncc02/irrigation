from fastapi import APIRouter, HTTPException, Query, Response
from typing import List, Dict
from app.models.models import SensorRecord
from math import ceil
from datetime import datetime, timedelta
from pymongo import MongoClient
from config import MONGODB_URI
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Kết nối MongoDB
client = MongoClient(MONGODB_URI)
db = client['irrigation']  # Sửa lại tên database
collection = db['soil_sensor_raw']  # Sửa lại tên collection

# Hàm helper để tính toán phân trang
def calculate_pagination(total_records: int, page: int, page_size: int) -> tuple:
    total_pages = ceil(total_records / page_size)
    
    if page > total_pages and total_pages > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Trang yêu cầu ({page}) vượt quá tổng số trang ({total_pages})"
        )
    
    skip = (page - 1) * page_size
    
    return total_records, total_pages, skip

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
        # Xây dựng query filter
        filter_query = {}
        if device_name:
            filter_query["deviceInfo.deviceName"] = device_name
        if start_time:
            filter_query["time"] = {"$gte": start_time.isoformat()}
        if end_time:
            if "time" in filter_query:
                filter_query["time"]["$lte"] = end_time.isoformat()
            else:
                filter_query["time"] = {"$lte": end_time.isoformat()}

        # Log query filter
        logger.info(f"Query filter: {filter_query}")

        # Đếm tổng số bản ghi
        total_records = collection.count_documents(filter_query)
        logger.info(f"Total records found: {total_records}")
        
        # Tính toán phân trang
        total_records, total_pages, skip = calculate_pagination(
            total_records, page, page_size
        )
        
        # Lấy dữ liệu từ MongoDB
        cursor = collection.find(filter_query).sort("time", -1).skip(skip).limit(page_size)
        sensor_records = []
        for doc in cursor:
            try:
                logger.info(f"Processing document: {doc}")
                sensor_record = SensorRecord(**doc)
                sensor_records.append(sensor_record)
            except Exception as e:
                logger.error(f"Error processing document: {e}")
                continue
        
        # Thêm thông tin phân trang vào header
        response.headers["X-Total-Records"] = str(total_records)
        response.headers["X-Total-Pages"] = str(total_pages)
        response.headers["X-Current-Page"] = str(page)
        response.headers["X-Page-Size"] = str(page_size)
        
        return sensor_records
        
    except Exception as e:
        logger.error(f"Error in get_sensor_data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sensors/{deduplication_id}", response_model=SensorRecord)
async def get_sensor_by_id(deduplication_id: str):
    try:
        # Tìm bản ghi theo deduplicationId trong MongoDB
        record = collection.find_one({"deduplicationId": deduplication_id})
        
        if record:
            return SensorRecord(**record)
            
        # Nếu không tìm thấy
        raise HTTPException(status_code=404, detail=f"Không tìm thấy bản ghi với ID: {deduplication_id}")
        
    except Exception as e:
        logger.error(f"Error in get_sensor_by_id: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    
    
# // ...existing code...

# @router.delete("/sensors/delete-oldest")
# async def delete_oldest_sensor():
#     try:
#         # Đếm tổng số bản ghi
#         total_records = collection.count_documents({})
        
#         if total_records <= 2:
#             raise HTTPException(
#                 status_code=400,
#                 detail="Không thể xóa vì số lượng sensor records hiện tại không vượt quá 2"
#             )
            
#         # Tìm bản ghi cũ nhất dựa trên trường time
#         oldest_record = collection.find_one({}, sort=[("time", 1)])
        
#         if oldest_record:
#             # Xóa bản ghi cũ nhất
#             result = collection.delete_one({"_id": oldest_record["_id"]})
            
#             if result.deleted_count > 0:
#                 logger.info(f"Đã xóa sensor record cũ nhất với ID: {oldest_record['_id']}")
#                 return {
#                     "message": "Xóa thành công sensor record cũ nhất",
#                     "deleted_record_id": str(oldest_record["_id"]),
#                     "total_records_remaining": total_records - 1
#                 }
        
#         raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi để xóa")
        
#     except HTTPException as http_ex:
#         raise http_ex
#     except Exception as e:
#         logger.error(f"Error in delete_oldest_sensor: {e}")
#         raise HTTPException(status_code=500, detail=str(e))