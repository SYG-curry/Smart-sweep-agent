from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel, Field


# 泛型类
T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    code: int = Field(default=200, description="状态码")
    message: str = Field(default="success", description="提示信息")
    data: Optional[T] = Field(default=None, description="响应数据")
    request_id: Optional[str] = Field(default=None, description="请求ID")
    elapsed_ms: Optional[float] = Field(default=None, description="处理耗时(毫秒)")

    # 在生成 OpenAPI 文档（也就是 /docs 页面）时，为这个模型附加一个示例 JSON，方便前端或其他人直观地看到返回结构
    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "message": "success",
                "data": {},
                "request_id": "1234567890",
                "elapsed_ms": 100.0
            }
        }

class ChatData(BaseModel):
    answer: str = Field(..., description="智能客服回答")
    session_id: str = Field(..., description="会话ID")
    sources: Optional[list] = Field(default=None, description="参考来源")

# ChatData是Generic[T], 填充data
class ChatApiResponse(ApiResponse[ChatData]):
    pass

class ErrorResponse(BaseModel):
    code: int = Field(..., description="错误码")
    message: str = Field(..., description="错误信息")
    data: Optional[Any] = Field(default=None, description="错误详情")
    request_id: Optional[str] = Field(default=None, description="请求ID")










