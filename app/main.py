from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import irrigation, sensors

app = FastAPI(
    title="Hệ thống dự đoán tưới nước và bón phân",
    description="API dự đoán tưới nước và bón phân dựa trên dữ liệu cảm biến",
    version="1.0.0"
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả các nguồn
    allow_credentials=True,
    allow_methods=["*"],  # Cho phép tất cả các phương thức
    allow_headers=["*"],  # Cho phép tất cả các header
)

# Đăng ký router
app.include_router(irrigation.router, prefix="/api", tags=["irrigation"])
app.include_router(sensors.router, prefix="/api", tags=["sensors"])

# Endpoint kiểm tra sức khỏe
@app.get("/health")
async def health_check():
    return {"status": "healthy"} 