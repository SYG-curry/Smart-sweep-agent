import time, uuid, session.models
from api.context import request_id_var, request_start_time_var
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from api.exceptions.business import BusinessException
from api.middleware.middleware import LoggingMiddleware
from api.routers import health, chat, auth
from utils.db import Base, engine
from utils.logger_handler import logger
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="SmartSweepAgent API",
    description="智扫通机器人智能客服后端服务",
    version="0.5.0",
)

# 开发阶段允许所有来源, 生产环境换成具体域名
origins = [
    "http://localhost:5173",    # vite默认端口
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "http://127.0.1:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # 允许的来源
    allow_credentials=True,     # 允许携带 Cookie (JWT 存 Cookie 时需要)
    allow_methods=["*"],        # 允许所有 HTTP 方法(GET……)
    allow_headers=["*"],        # 允许所有的请求头(包括 Authorization)
)

# 自动创建所有的表
Base.metadata.create_all(bind=engine)

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

app.add_middleware(LoggingMiddleware)

# 注册HTTP 中间件，对所有进入应用的请求都生效
@app.middleware("http")
async def add_request_context(request: Request, call_next):
    # 从请求头X-Request-ID中提取请求ID, 若没有则用UUID前8位生成
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
    # 将二者存入ContextVar, 供后续业务逻辑和异常处理器使用
    request_id_var.set(request_id)
    request_start_time_var.set(time.time())

    # 调用下一个中间件或路由
    response = await call_next(request)

    # 响应返回前, 把request_id 和 请求耗时 写入响应头
    response.headers["X-Request-ID"] = request_id
    elapsed = (time.time() - request_start_time_var.get()) * 1000
    response.headers["X-Elapsed-Ms"] = f"{elapsed:.2f}"

    return response

# 捕获业务异常
@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    request_id = request_id_var.get()
    elapsed = (time.time() - request_start_time_var.get()) * 1000

    logger.warning(f"[business_error] code={exc.code}, message={exc.message}, request_id={request_id}")

    return JSONResponse(
        status_code=exc.code if 400 <= exc.code < 600 else 400,
        content={
            "code": exc.code,
            "message": exc.message,
            "data": exc.data,
            "request_id": request_id,
            "elapsed_ms": round(elapsed, 2)
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = request_id_var.get()
    elapsed = (time.time() - request_start_time_var.get()) * 1000

    logger.error(f"[server_error] {type(exc).__name__}: {exc}, request_id={request_id}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "服务内部错误",
            "data": {"error": str(exc)},
            "request_id": request_id,
            "elapsed_ms": round(elapsed, 2)
        }
    )

@app.get("/")
def root():
    return {
        "message": "SmartSweepAgent API is running",
        "version": "0.5.0",
        "docs": "/docs",
        "health": "/api/health",
        "chat": "/api/chat",
    }






