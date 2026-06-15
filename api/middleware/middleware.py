import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from utils.logger_handler import logger



class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time
        logger.info(f"{request.method} {request.url.path} completed in {process_time:.3f}s")

        return response









