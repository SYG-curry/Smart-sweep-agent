"""
   定义请求结构
   定义响应结构
   避免接口里到处些裸字典
"""
from typing import Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str = Field(..., description="用户输入的问题")
    session_id: Optional[str] = Field(default=None, description="会话ID")


class ChatResponse(BaseModel):
    answer: str = Field(..., description="智能客服回答")
    session_id: str = Field(..., description="会话ID")


class ChatMessageResponse(BaseModel):
    role: str = Field(..., description="消息角色, user or assistant")
    content: str = Field(..., description="消息内容")



