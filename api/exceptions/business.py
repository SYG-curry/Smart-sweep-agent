from typing import Any, Optional



class BusinessException(Exception):
    def __init__(
            self,
            code: int,
            message: str,
            data: Optional[Any] = None,
    ):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(message)

class RateLimitException(BusinessException):
    def __init__(self, message: str = "请求过于频繁, 请稍后再试"):
        super().__init__(code=429, message=message)

class SessionNotFoundException(BusinessException):
    def __init__(self, session_id: str):
        super().__init__(
            code=404,
            message=f"会话不存在: {session_id}",
            data={"session_id": session_id},
        )

class RAGException(BusinessException):
    def __init__(self, message: str = "知识库检索失败"):
        super().__init__(code=500, message=message)

class AgentException(BusinessException):
    def __init__(self, message: str = "智能体执行失败"):
        super().__init__(code=500, message=message)

class ForbiddenException(BusinessException):
    def __init__(self, message: str = "无权限访问该资源"):
        super().__init__(code=403, message=message)

class UnauthorizedException(BusinessException):
    def __init__(self, message: str = "请先登录"):
        super().__init__(code=401, message=message)









