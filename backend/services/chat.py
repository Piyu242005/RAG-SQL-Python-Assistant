import logging
import time
import json
import hashlib
from typing import AsyncGenerator, List, Optional, Dict, Any
from core.config import settings
from providers.base import BaseLLMProvider
from retrieval.engine import RetrievalEngine
from cache.redis import RedisCache
from memory.session import SessionMemory
from schemas.chat import SourceMetadata, StreamChunk
from langchain_core.documents import Document

logger = logging.getLogger("chat-service")

class ChatService:
    """Orchestrates the RAG chat pipeline."""
    
    def __init__(
        self, 
        llm: BaseLLMProvider, 
        retrieval: RetrievalEngine,
        cache: RedisCache,
        memory: SessionMemory
    ):
        self.llm = llm
        self.retrieval = retrieval
        self.cache = cache
        self.memory = memory

    async def chat(self, question: str, session_id: str = "default") -> Dict[str, Any]:
        """Process a chat query and return a full response."""
        # Check cache
        cache_key = self._generate_cache_key(question, session_id, None)
        if settings.enable_cache:
            cached = self.cache.get(cache_key)
            if cached:
                return {"answer": cached["answer"], "sources": cached["sources"], "success": True}

        # Retrieval
        retriever = self.retrieval.get_hybrid_retriever(k=8)
        docs = await self._get_docs(retriever, question)
        context_text = self._format_docs(docs)
        sources = self._extract_sources(docs)

        # Generation
        history = self.memory.get_history(session_id)
        prompt = self._build_prompt(question, context_text, history.messages)
        answer = await self.llm.generate(prompt)

        # History and Cache
        if settings.enable_cache:
            self.cache.set(cache_key, {"answer": answer, "sources": sources})
        
        history.add_user_message(question)
        history.add_ai_message(answer)

        return {"answer": answer, "sources": sources, "success": True}

    async def stream_chat(self, question: str, session_id: str = "default") -> AsyncGenerator[str, None]:
        start_time = time.time()
        
        # 1. History Management
        self.memory.trim_history(session_id, settings.max_history_messages)
        history = self.memory.get_history(session_id)
        
        # 2. Cache Lookup
        cache_key = self._generate_cache_key(question, session_id, history)
        if settings.enable_cache:
            cached = self.cache.get(cache_key)
            if cached:
                logger.info(f"Cache hit for {question}")
                yield f"data: {json.dumps({'sources': cached['sources']})}\n\n"
                for char in cached["answer"]:
                    yield f"data: {json.dumps({'token': char})}\n\n"
                yield "data: [DONE]\n\n"
                return

        # 3. Retrieval
        retriever = self.retrieval.get_hybrid_retriever(k=8)
        docs = await self._get_docs(retriever, question)
        
        # 4. Context Preparation
        context_text = self._format_docs(docs)
        sources = self._extract_sources(docs)
        
        yield f"data: {json.dumps({'sources': sources})}\n\n"

        # 5. Generation
        prompt = self._build_prompt(question, context_text, history.messages)
        full_answer = ""
        async for token in self.llm.stream(prompt):
            full_answer += token
            yield f"data: {json.dumps({'token': token})}\n\n"

        # 6. Post-processing
        if settings.enable_cache:
            self.cache.set(cache_key, {"answer": full_answer, "sources": sources})
        
        history.add_user_message(question)
        history.add_ai_message(full_answer)
        
        # Send final summary for frontend compatibility
        yield f"data: {json.dumps({'answer': full_answer, 'sources': sources})}\n\n"
        yield "data: [DONE]\n\n"

    def _generate_cache_key(self, question: str, session_id: str, history: Any) -> str:
        version = self.cache.get_version()
        q_hash = hashlib.md5(question.strip().lower().encode()).hexdigest()[:16]
        return f"rag_cache:{session_id}:{version}:{q_hash}"

    async def _get_docs(self, retriever: Any, query: str) -> List[Document]:
        # Implementation of retrieval with deduplication and trimming
        # (Simplified for now, can be more complex)
        docs = retriever.invoke(query)
        return docs[:5]

    def _format_docs(self, docs: List[Document]) -> str:
        formatted = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get('source', 'Unknown')
            page = doc.metadata.get('page', 'N/A')
            formatted.append(f"--- Doc {i} (Source: {source}, Page: {page}) ---\n{doc.page_content}\n")
        return "\n".join(formatted)

    def _extract_sources(self, docs: List[Document]) -> List[Dict[str, Any]]:
        sources = []
        seen = set()
        for doc in docs:
            key = f"{doc.metadata.get('source')}_{doc.metadata.get('page')}"
            if key not in seen:
                sources.append({
                    "source": doc.metadata.get('source', 'Unknown'),
                    "page": doc.metadata.get('page', 'N/A')
                })
                seen.add(key)
        return sources

    def _build_prompt(self, question: str, context: str, history: List[Any]) -> str:
        # Prompt management can move to prompts/ later
        history_text = "\n".join([f"{m.type}: {m.content}" for m in history[-5:]])
        return f"""Use the context below to answer the question.
Context:
{context}

History:
{history_text}

Question: {question}
Answer:"""
