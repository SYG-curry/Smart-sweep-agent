import json
import hashlib
from typing import Any, Optional
from utils.redis_client import get_redis, redis_conf
from utils.logger_handler import logger


# Cache相关
class CacheService:
    # 这个注解相比 classmethod 不能取成员变量, 更像一个纯工具调用类
    @staticmethod
    # *args: 可变参数(可以为任意数目的参数)
    def _get_cache_key(prefix: str, *args) -> str:
        raw = ":".join(str(arg) for arg in args)
        # 取16机制哈希加密过的key, 截断前16个字符, 防止过长
        hash_part = hashlib.md5(raw.encode("utf-8")).hexdigest()[:16]
        return f"{prefix}:{hash_part}"

    @staticmethod
    def get(prefix: str, *args) -> Optional[Any]:
        client = get_redis()
        if not client:
            return None

        key = CacheService._get_cache_key(prefix, *args)
        try:
            value = client.get(key)
            if value:
                logger.debug(f"[cache] 命中缓存: {key}")
                # 将value反序列化成原类型数据
                return json.loads(value)
        except Exception as e:
            logger.error(f"[cache] 获取缓存失败: {e}")
        return None

    @staticmethod
    def set(prefix: str, *args, value: Any, ttl: Optional[int] = None):
        client = get_redis()
        if not client:
            return

        key = CacheService._get_cache_key(prefix, *args)
        try:
            if ttl is None:
                # {} 在这里是一个“安全垫”，防止配置文件缺失 cache 段时引发崩溃，让程序在完全没有配置时也能优雅地使用默认值。
                ttl = redis_conf.get("cache", {}).get("rag_ttl", 300)
            # setex = set + expire
            # json.dumps(value, ensure_ascii=False)：把对象（字典、列表等）转为 JSON 字符串存储，
            # ensure_ascii=False 保证中文不会被转成 \uxxxx 格式。
            client.setex(key, ttl, json.dumps(value, ensure_ascii=False))
            logger.debug(f"[cache] 写入缓存: {key}, ttl={ttl}")
        except Exception as e:
            logger.warning(f"[cache] 写入缓存失败: {e}")

    @staticmethod
    def delete(prefix: str, *args):
        client = get_redis()
        if not client:
            return

        key = CacheService._get_cache_key(prefix, *args)
        try:
            client.delete(key)
            logger.debug(f"[cache] 删除缓存: {key}")
        except Exception as e:
            logger.warning(f"[cache] 删除缓存失败: {e}")

cache_service = CacheService()











