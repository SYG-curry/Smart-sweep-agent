from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from utils.config_handler import auth_conf


# 创建JWT
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    # 计算过期时间
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=auth_conf.get("access_token_expire_minutes", 60))
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        # 用 密钥 和 签名 对JWT进行签名
        auth_conf.get("secret_key"),
        algorithm=auth_conf.get("algorithm")
    )

# 验证JWT
def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(
            token,
            auth_conf.get("secret_key"),
            algorithms=[auth_conf.get("algorithm")]
        )
    # 签名无效, token格式错误, 过期, 算法不匹配等等, 全部返回None
    except JWTError:
        return None








