import logging
from typing import Dict, Any, List
from langchain_community.chat_message_histories import ChatMessageHistory, RedisChatMessageHistory
from core.config import settings

logger = logging.getLogger("session-memory")

class SessionMemory:
    """Manages session-based chat history."""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url
        self.in_memory_history: Dict[str, ChatMessageHistory] = {}

    def get_history(self, session_id: str):
        if self.redis_url:
            try:
                return RedisChatMessageHistory(
                    session_id=f"chat_history:{session_id}",
                    url=self.redis_url,
                    ttl=86400
                )
            except Exception as e:
                logger.warning(f"Redis history failed, falling back to memory: {e}")
        
        if session_id not in self.in_memory_history:
            self.in_memory_history[session_id] = ChatMessageHistory()
        return self.in_memory_history[session_id]

    def trim_history(self, session_id: str, max_messages: int):
        history = self.get_history(session_id)
        if len(history.messages) > max_messages:
            keep = history.messages[-max_messages:]
            history.clear()
            for msg in keep:
                if msg.type == "human":
                    history.add_user_message(msg.content)
                else:
                    history.add_ai_message(msg.content)
            logger.info(f"History trimmed for session {session_id}")
