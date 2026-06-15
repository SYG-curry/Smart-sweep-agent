import uuid
from datetime import timedelta
from fastapi import APIRouter, Depends
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from api.dependencies.auth import get_current_user
from api.exceptions.business import BusinessException
from api.context import request_id_var
from api.schemas.auth import LoginRequest, RegisterRequest, TokenData, UserInfo
from api.schemas.response import ApiResponse
from session.session_manager import session_manager
from utils.config_handler import auth_conf
from utils.db import get_db
from utils.jwt_handler import create_access_token



router = APIRouter()
# CryptContext: 创建一个密码管理上下文, schemes: 用bcrypt加密算法, deprecated: 允许以后升级加密方案时, 自动识别旧密码并逐步迁移
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/register", response_model=ApiResponse, status_code=201)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    existing = session_manager.get_user_by_username(db=db, username=request.username)
    if existing:
        raise BusinessException(code=409, message="用户名已存在")

    user = session_manager.create_user(
        db=db,
        user_id=str(uuid.uuid4()),
        username=request.username,
        password_hash=pwd_context.hash(request.password),
    )

    return ApiResponse(
        code=201,
        message="注册成功",
        data={"user_id": user.id, "username": user.username},
        request_id=request_id_var.get(),
    )

@router.post("/login", response_model=ApiResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = session_manager.get_user_by_username(db=db, username=request.username)

    if not user or not pwd_context.verify(request.password, user.password_hash):
        raise BusinessException(code=401, message="用户名或密码错误")

    if not user.is_active:
        raise BusinessException(code=403, message="账号已禁用")

    expire_minutes = auth_conf.get("access_token_expire_minutes", 60)
    access_token = create_access_token(
        data={"sub": user.id, "username": user.username},
        expires_delta=timedelta(minutes=expire_minutes),
    )

    return ApiResponse(
        code=200,
        message="登录成功",
        data=TokenData(
            access_token=access_token,
            token_type="bearer",
            expires_in=expire_minutes * 60,
        ),
        request_id=request_id_var.get(),
    )

@router.get("/me", response_model=ApiResponse)
def get_me(current_user = Depends(get_current_user)):
    return ApiResponse(
        code=200,
        message="获取用户信息成功",
        data=UserInfo(
            user_id=current_user.id,
            username=current_user.username,
            created_at=current_user.created_at.isoformat(),
        ),
        request_id=request_id_var.get(),
    )

















