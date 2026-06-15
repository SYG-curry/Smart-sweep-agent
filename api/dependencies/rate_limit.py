from fastapi import Request, HTTPException
from utils.redis_client import get_redis, redis_conf
from utils.logger_handler import logger



class RateLimiter:
    def __init__(
            self,
            max_requests: int = None,
            window_seconds: int = None,
    ):
        cache_conf = redis_conf.get("cache", {}) if redis_conf else {}
        self.max_requests = max_requests or cache_conf.get("rate_limit_max_requests", 10)
        self.window_seconds = window_seconds or cache_conf.get("rate_limit_ttl", 60)

    def _get_client_ip(self, request: Request) -> str:
        # request 是一个 FastAPI/Starlette 的 Request 对象
        # headers 是一个字典，包含所有 HTTP 请求头
        # X-Forwarded-For 是一个 HTTP 标准请求头. 当用户经过代理服务器（如 Nginx、负载均衡器）访问时，代理会把用户的真实 IP 追加到这个头里
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # 这个头的值可能是一个 IP 列表，像 "用户IP, 代理1IP, 代理2IP", 取第一个: 最原始的客户端IP
            return forwarded.split(",")[0].strip()
        # 如果没有 X-Forwarded-For 头，说明是客户端直连你的服务器
        # request.client 是一个包含直连连接信息的对象，其 host 属性就是连接的远端 IP
        return request.client.host if request.client else "unknown"

    async def __call__(self, request: Request):
        client = get_redis()
        if not client:
            return

        client_ip = self._get_client_ip(request)
        # request.url 是一个 URL 对象，它把请求的整个网址拆解成了各个部分，像下面这样：
        # 假设完整请求是 https://example.com/api/chat?q=你好，那么 request.url 的属性包括：
        # .scheme："https"
        # .hostname："example.com"
        # .path："/api/chat"
        # .query："q=你好"
        path = request.url.path
        key = f"rate_limit:{client_ip}:{path}"

        try:
            current = client.get(key)

            if current is None:
                client.setex(key, self.window_seconds, 1)
            elif int(current) >= self.max_requests:
                logger.warning(f"[rate_limit]限流触发: ip={client_ip}, path={path}")
                raise HTTPException(
                    status_code=429,
                    detail={
                        "code": 429,
                        "message": "请求过于繁忙, 请稍后再试",
                        "data": {
                            "retry_after": self.window_seconds,
                        },
                    },
                )
            else:
                client.incr(key)
        except HTTPException as e:
            raise
        except Exception as e:
            logger.warning(f"[rate_limit]限流异常: {e}")

rate_limit = RateLimiter()



















