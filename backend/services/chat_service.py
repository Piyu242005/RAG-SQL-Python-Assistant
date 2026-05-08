from retrieval.engine import HybridRetriever
from providers.ollama import OllamaProvider
from cache.semantic_cache import SemanticCache
from memory.session import SessionManager
import logging

class ChatService:
    def __init__(self):
        self.retriever = HybridRetriever()
        self.llm = OllamaProvider()
        self.cache = SemanticCache()
        self.session_manager = SessionManager()

    async def stream(self, question: str, session_id: str = "default"):
        logging.info(f"Processing question: {question}")
        
        # 1. Check Cache
        cached_response = self.cache.get(question)
        if cached_response:
            logging.info("Cache hit!")
            yield cached_response
            return

        # 2. Get History (for future context-aware chat)
        history = self.session_manager.get_history(session_id)
        
        # 3. Retrieve relevant documents
        docs = await self.retriever.retrieve(question)
        
        # 4. Construct context
        context = "\n\n".join([d.page_content for d in docs])
        
        # 5. Create prompt
        prompt = f"""You are a professional Enterprise Assistant. Use the provided context to answer the user's question accurately.

Context:
{context}

Question:
{question}

Answer:"""

        # 6. Stream and Collect
        full_response = ""
        async for token in self.llm.stream(prompt):
            full_response += token
            yield token
        
        # 7. Update Cache and History
        if full_response:
            self.cache.set(question, full_response)
            if history:
                history.add_user_message(question)
                history.add_ai_message(full_response)
