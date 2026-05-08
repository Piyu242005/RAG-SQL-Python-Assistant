import redis
import json
import logging
from typing import Optional, Any
from core.config import settings

logger = logging.getLogger("redis-cache")

class RedisCache:
    """Handles Redis-based caching."""
    
    def __init__(self):
        self.url = settings.redis_url
        try:
            self.client = redis.from_url(
                self.url, 
                decode_responses=True,
                socket_timeout=5,
                retry_on_timeout=True
            )
            logger.info(f"Connected to Redis at {self.url}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.client = None

    def set(self, key: str, value: Any, expire_seconds: Optional[int] = None):
        if not self.client:
            return
        ttl = expire_seconds or settings.redis_cache_ttl_sec
        try:
            serialized = json.dumps(value)
            self.client.set(key, serialized, ex=ttl)
        except Exception as e:
            logger.error(f"Redis set error: {e}")

    def get(self, key: str) -> Optional[Any]:
        if not self.client:
            return None
        try:
            value = self.client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    def get_version(self) -> int:
        if not self.client:
            return 0
        try:
            version = self.client.get("rag_cache_version")
            return int(version) if version else 0
        except Exception:
            return 0

    def increment_version(self) -> int:
        if not self.client:
            return 0
        try:
            return self.client.incr("rag_cache_version")
        except Exception:
            return 0
