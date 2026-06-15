from pydantic import BaseModel, Field



class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=64, description="用户名")
    password: str = Field(..., min_length=6, description="密码, 至少6位")

class LoginRequest(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")

class TokenData(BaseModel):
    access_token: str = Field(..., description="JWT token")
    token_type: str = Field(default="bearer", description="token类型")
    expires_in: int = Field(..., description="token过期时间(秒)")

class UserInfo(BaseModel):
    user_id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    created_at: str = Field(..., description="注册时间")











