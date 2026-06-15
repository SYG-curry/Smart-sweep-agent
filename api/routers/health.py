"""
    验证服务是否启动成功
"""
from fastapi import FastAPI, APIRouter

router = APIRouter()

@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "服务正常"
    }

