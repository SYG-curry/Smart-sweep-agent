import time
from typing import Optional
import redis
import yaml
from utils.path_tool import get_abs_path
from utils.logger_handler import logger


# Redis相关
def load_redis_config():
    config_path = get_abs_path("config/redis.yml")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.warning(f"[redis_client] Redis配置文件不存在:{config_path}")
        return None

redis_conf = load_redis_config()

class RedisClient:
    # 类内部使用，不建议外部直接访问(约定俗称, python无私有变量)
    _instance: Optional[redis.Redis] = None
    _available: bool = False
    # 上一次连接失败的时间
    _last_failed_at: float = 0
    # 失败后多少秒内不再重试Redis
    _retry_interval: int = 30

    """
    @classmethod 是类方法装饰器，它把方法变成操作类本身，而不是操作实例。
    参数 cls 代表类本身（类似实例方法的 self 代表实例）。
    @classmethod
    def get_client(cls) -> Optional[redis.Redis]:
        if cls._instance is not None:
    方法内部直接操作 cls._instance、cls._available 这些类变量。
    因为我们希望全局只有一个 Redis 连接，这个状态应该属于类，而不是某个实例。你无需先创建 RedisClient 对象再调用方法，
    直接 RedisClient.get_client() 即可，这更符合单例模式的使用习惯。
    """
    @classmethod
    def get_client(cls) -> Optional[redis.Redis]:
        now = time.time()

        # 如果上次失败距离现在不到30秒, 直接降级, 不再阻塞ping
        # 优化的意义: 1. Redis在很多地方都有使用, 比如rate_limit, RAG cache等, 这样如果Redis失效每个地方都需要等待超时拖累时间
        # 2. 减少Redis连接失败的次数, 避免每次请求都去重连Redis, 第一次失败后的30s内都可以直接返回None, 不会卡, 30s之后再尝试恢复
        if not cls._available and cls._last_failed_at:
            if now - cls._last_failed_at < cls._retry_interval:
                return None

        if cls._instance is not None and cls._available:
            return cls._instance

        if not redis_conf:
            cls._available = False
            cls._last_failed_at = now
            return None

        try:
            redis_params = {
                "host": redis_conf.get("host", "localhost"),
                "port": redis_conf.get("port", 6379),
                "db": redis_conf.get("db", 0),
                "decode_responses": redis_conf.get("decode_responses", True),       # 自动将 bytes 解码成字符串
                "socket_connect_timeout": 2,    # 建立 TCP 连接的超时时间, 快速失败
                "socket_timeout": 2,        # 连接建立后, 读写操作过期时间
                "protocol": 2,       # 强制使用RESP2协议, RESP3协议不支持
            }

            # 只有密码为非空时才添加 password 参数, 以防 redis 无密码情况
            password = redis_conf.get("password")
            if password:
                redis_params["password"] = password
            cls._instance = redis.Redis(**redis_params)
            cls._instance.ping()
            cls._available = True
            cls._last_failed_at = 0
            logger.info("[redis_client] Redis连接成功")
            return cls._instance
        except Exception as e:
            logger.warning(f"[redis_client] Redis 连接失败, 将使用降级模式: {e}")
            cls._instance = None
            cls._available = False
            cls._last_failed_at = now
            return None

    @classmethod
    def is_available(cls) -> bool:
        if cls._instance is None:
            cls.get_client()
        return cls._available

def get_redis() -> Optional[redis.Redis]:
    return RedisClient.get_client()












