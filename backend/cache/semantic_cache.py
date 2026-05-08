import redis
import hashlib
import json
import logging

class SemanticCache:
    def __init__(self, host="localhost", port=6379):
        try:
            self.redis = redis.Redis(host=host, port=port, decode_responses=True)
            self.redis.ping()
        except Exception as e:
            logging.warning(f"Redis not available for caching: {e}")
            self.redis = None

    def _get_key(self, query: str):
        # In a real system, we'd use embedding similarity for semantic cache.
        # Here we use hash for exact/near-exact matches.
        digest = hashlib.sha256(query.lower().strip().encode()).hexdigest()
        return f"rag:cache:{digest}"

    def get(self, query: str):
        if not self.redis: return None
        key = self._get_key(query)
        cached = self.redis.get(key)
        return json.loads(cached) if cached else None

    def set(self, query: str, response: str, ttl: int = 3600):
        if not self.redis: return
        key = self._get_key(query)
        self.redis.setex(key, ttl, json.dumps(response))
