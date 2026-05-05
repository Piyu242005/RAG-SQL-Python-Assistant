"""Redis connection management for caching and chat history."""
import redis
import json
import logging
from typing import Optional, Any
from config import settings

logger = logging.getLogger("redis-manager")

class RedisManager:
    """Manage Redis connections and operations."""
    
    def __init__(self):
        """Initialize Redis connection."""
        self.url = settings.redis_url
        try:
            self.client = redis.from_url(
                self.url, 
                decode_responses=True,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Test connection
            self.client.ping()
            logger.info(f"Connected to Redis at {self.url}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.client = None

    def get_client(self) -> Optional[redis.Redis]:
        """Get the Redis client."""
        return self.client

    def set_cache(self, key: str, value: Any, expire_seconds: Optional[int] = None):
        """Set a value in cache with expiration."""
        if not self.client:
            return
            
        ttl = expire_seconds if expire_seconds is not None else settings.redis_cache_ttl_sec
            
        try:
            serialized = json.dumps(value)
            self.client.set(key, serialized, ex=ttl)
        except Exception as e:
            logger.error(f"Redis set_cache error: {e}")

    def get_cache(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        if not self.client:
            return None
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Redis get_cache error: {e}")
        return None

    def get_cache_version(self) -> int:
        """Retrieve the current global cache version, creating it if missing."""
        if not self.client:
            return 0
        try:
            version = self.client.get("rag_cache_version")
            if version is None:
                self.client.set("rag_cache_version", 0)
                return 0
            return int(version)
        except Exception as e:
            logger.error(f"Redis get_cache_version error: {e}")
            return 0

    def increment_cache_version(self) -> int:
        """Atomically increment the cache version and return the new value."""
        if not self.client:
            return 0
        try:
            new_version = self.client.incr("rag_cache_version")
            logger.info(f"[OK] Cache version incremented to {new_version}")
            return new_version
        except Exception as e:
            logger.error(f"Redis increment_cache_version error: {e}")
            return self.get_cache_version()

# Global instance
redis_manager = RedisManager()

def get_redis():
    """Dependency for getting Redis client."""
    return redis_manager.get_client()
