from langchain_community.chat_message_histories import RedisChatMessageHistory
import logging

class SessionManager:
    def __init__(self, redis_url="redis://localhost:6379"):
        self.redis_url = redis_url

    def get_history(self, session_id: str):
        try:
            return RedisChatMessageHistory(
                session_id=session_id,
                url=self.redis_url,
                ttl=86400 # 24 hours
            )
        except Exception as e:
            logging.error(f"Failed to load chat history: {e}")
            return None
