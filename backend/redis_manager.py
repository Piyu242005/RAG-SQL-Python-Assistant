"""Backward compatibility adapter for RedisManager."""
from cache.redis import RedisCache

# Create a global instance to match existing usage
_cache = RedisCache()

class RedisManager:
    def __init__(self):
        self.client = _cache.client
        self.url = _cache.url

    def get_client(self):
        return _cache.client

    def set_cache(self, key, value, expire_seconds=None):
        _cache.set(key, value, expire_seconds)

    def get_cache(self, key):
        return _cache.get(key)

    def get_cache_version(self):
        return _cache.get_version()

    def increment_cache_version(self):
        return _cache.increment_version()

redis_manager = RedisManager()

def get_redis():
    return redis_manager.get_client()
