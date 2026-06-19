from typing import Optional
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from session.session_manager import session_manager
from utils.db import get_db
from utils.jwt_handler import decode_access_token


# FastAPI内置安全工具类, 专用于解析HTTP请求头里的Authorization: Bearer
# auto_error=False: 禁用自动抛出异常, 若不设置, 只要请求没有提供Authorization头, 就会抛出异常
# HTTPBearer是一个类, Depends()会自动调用HTTPBearer的__call__方法
security = HTTPBearer(auto_error=False)

# 强制性认证(必须登录才能使用的接口)
def get_current_user(
        # HTTPAuthorizationCredentials: HTTPBearer解析成功后返回的数据结构
        # 主要包含: 1. credentials.scheme(通常是Bearer)   2. credentials.credentials(真正的token字符串)
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
        db: Session = Depends(get_db),
):
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail={"code": 401, "message": "未提供认证令牌"},
        )

    payload = decode_access_token(credentials.credentials)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail={"code": 401, "message": "令牌无效或已过期"},
        )

    # sub指的是subject, 用来标识当前用户, 行业规范
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail={"code": 401, "message": "令牌数据异常"},
        )

    user = session_manager.get_user(db=db, user_id=user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=401,
            detail={"code": 401, "message": "用户不存在或已禁用"},
        )

    return user

# 可选性认证(支持匿名访问, 又想给登录用户提供额外功能的接口)
def get_current_user_optional(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
        db: Session = Depends(get_db),
):
    if not credentials:
        return None

    payload = decode_access_token(credentials.credentials)

    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    user = session_manager.get_user(db=db, user_id=user_id)
    if not user or not user.is_active:
        return None

    return user
