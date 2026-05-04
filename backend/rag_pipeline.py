"""RAG pipeline implementation with Redis and optimized retrieval."""
import asyncio
import logging
import json
import time
from typing import List, Dict, Optional, Any
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory, RedisChatMessageHistory
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import OllamaLLM as Ollama
try:
    from langchain.retrievers import ContextualCompressionRetriever
except ImportError:
    from langchain_classic.retrievers import ContextualCompressionRetriever

try:
    from langchain.retrievers.document_compressors import FlashrankRerank
except ImportError:
    from langchain_community.document_compressors import FlashrankRerank

from vector_store import VectorStoreManager
from llm_config import OllamaManager
from redis_manager import redis_manager
from config import settings

logger = logging.getLogger("rag-pipeline")

class RAGPipeline:
    """Optimized RAG pipeline with Redis caching and persistent history."""
    
    def __init__(self):
        """Initialize RAG pipeline."""
        self.vector_store_manager = VectorStoreManager()
        self.ollama_manager = OllamaManager()
        self.llm = None
        self.retriever = None
        self.chain = None
        self.in_memory_history = {} # Fallback
        
        # Initialize components
        self._initialize_llm()
        self._initialize_retriever(use_hybrid=True)
        self._initialize_reranker()
        self._initialize_chain()
    
    def _initialize_llm(self):
        """Initialize Ollama LLM with optimized parameters."""
        logger.info("Initializing Ollama LLM...")
        self.llm = Ollama(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            temperature=0.1,  
            num_ctx=4096,     
            num_predict=1024,
            top_k=20,
            top_p=0.9,
            repeat_penalty=1.1,
        )
        logger.info("[OK] LLM initialized (num_ctx=4096)")
    
    def _initialize_retriever(self, use_hybrid: bool = True):
        """Initialize document retriever (Hybrid search)."""
        logger.info(f"Initializing {'hybrid ' if use_hybrid else ''}retriever...")
        self.vector_store_manager.initialize_vectorstore()
        
        if use_hybrid:
            # Context Guard: Use k=8 to prevent context overflow during reranker fallback
            self.base_retriever = self.vector_store_manager.get_hybrid_retriever(k=8)
        else:
            self.base_retriever = self.vector_store_manager.get_retriever(k=20, search_type="mmr")
        
        self.retriever = self.base_retriever
    
    def _initialize_reranker(self):
        """Initialize FlashRank reranker (Select top 5)."""
        logger.info("Initializing FlashRank reranker...")
        try:
            compressor = FlashrankRerank(model="ms-marco-MiniLM-L-12-v2", top_n=5)
            self.retriever = ContextualCompressionRetriever(
                base_compressor=compressor, 
                base_retriever=self.base_retriever
            )
            logger.info("[OK] Reranker initialized (Top 5)")
        except Exception as e:
            logger.error(f"[X] Failed to initialize reranker: {str(e)}")
            self.retriever = self.base_retriever
    
    def _initialize_chain(self):
        """Initialize RAG chain with improved prompt and Redis history."""
        logger.info("Initializing RAG chain...")
        
        system_prompt = """You are a senior SQL and Python technical assistant. 
Answer the question ONLY using the provided context. 

Rules:
1. If the information is not in the context, say exactly: "I'm sorry, but that information is not available in the provided documents."
2. Do NOT use outside knowledge or hallucinate.
3. Always include a concise code example if applicable (SQL or Python).
4. Use clear markdown formatting.
5. Provide a direct and professional answer.
6. Always cite the Source and Page number if available."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human", "Context:\n{context}\n\nQuestion: {question}\n\nAnswer:")
        ])
        
        self.base_chain = (
            prompt
            | self.llm
            | StrOutputParser()
        )
        
        # Redis Caching setup with graceful degradation
        self.redis_client = None
        self.redis_available = False
        try:
            import redis
            self.redis_client = redis.from_url(settings.redis_url)
            if self.redis_client.ping():
                self.redis_available = True
                print("[OK] Redis Cache: Active")
            else:
                print("[!] Redis Cache: Refused connection. Falling back to memory-only.")
        except Exception as e:
            print(f"[!] Redis Cache: Not available ({e}). Falling back to memory-only.")

        def get_session_history(session_id: str):
            if self.redis_available:
                return RedisChatMessageHistory(
                    session_id=f"chat_history:{session_id}",
                    url=settings.redis_url
                )
            else:
                if session_id not in self.in_memory_history:
                    self.in_memory_history[session_id] = ChatMessageHistory()
                return self.in_memory_history[session_id]

        self.chain = RunnableWithMessageHistory(
            self.base_chain,
            get_session_history,
            input_messages_key="question",
            history_messages_key="history",
        )
        logger.info("[OK] RAG chain initialized")
    
    def _format_docs(self, docs: List[Document]) -> str:
        formatted = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get('source', 'Unknown')
            page = doc.metadata.get('page', 'N/A')
            formatted.append(f"--- Document {i} (Source: {source}, Page: {page}) ---\n{doc.page_content}\n")
        return "\n".join(formatted)

    def _extract_text(self, content: Any) -> str:
        """Safely extract text from various LangChain/Ollama response types."""
        if isinstance(content, str):
            return content
        if isinstance(content, dict):
            # Try common keys used by different models/parsers
            for key in ['text', 'answer', 'content', 'output']:
                if key in content and isinstance(content[key], str):
                    return content[key]
            # Fallback to string representation of the dict
            return str(content)
        return str(content) if content is not None else ""

    async def _rewrite_query(self, query: str) -> str:
        """Improve query for search accuracy."""
        try:
            prompt = f"Improve this query for a semantic search engine. Make it concise and focused on keywords. Return ONLY the improved query: {query}"
            rewritten = await self.llm.ainvoke(prompt)
            return rewritten.content if hasattr(rewritten, 'content') else str(rewritten)
        except Exception:
            return query

    async def _expand_query(self, query: str) -> str:
        """Expands the user query using a HyDE-inspired approach for better retrieval."""
        try:
            expansion_prompt = f"Given the user query: '{query}', generate a short technical description of what the answer might look like to help with vector search. Keep it under 50 words."
            expansion = await self.llm.ainvoke(expansion_prompt)
            expanded_text = expansion.content if hasattr(expansion, 'content') else str(expansion)
            return f"{query} {expanded_text}"
        except Exception:
            return query

    def _deduplicate_docs(self, docs: List[Document]) -> List[Document]:
        """Removes duplicate documents and filters out low-relevancy noise."""
        seen_content = set()
        unique_docs = []
        for doc in docs:
            content_hash = hash(doc.page_content.strip())
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_docs.append(doc)
        return unique_docs

    def _trim_docs(self, docs: List[Document], max_tokens: int = 3000) -> List[Document]:
        """Trim docs at the document level to prevent semantic truncation."""
        total = 0
        result = []
        for d in docs:
            # Assuming ~4 chars per token
            tokens = len(d.page_content) // 4
            if total + tokens > max_tokens:
                break
            result.append(d)
            total += tokens
        return result

    async def _manage_history_size(self, session_id: str):
        """Safely clean up history before invoking the chain."""
        history = self.in_memory_history.get(session_id)
        if self.redis_available:
            history = RedisChatMessageHistory(
                session_id=f"chat_history:{session_id}",
                url=settings.redis_url
            )
            
        if history and len(history.messages) > settings.max_history_messages:
            logger.info(f"[*] Summarizing history for session {session_id}...")
            prompt = f"Summarize the following conversation history briefly: {history.messages}"
            summary = await self.llm.ainvoke(prompt)
            history.clear()
            history.add_user_message("Previous Conversation Summary:")
            history.add_ai_message(self._extract_text(summary))
            logger.info(f"[OK] History compressed.")

    async def stream_query(self, question: str, doc_type: Optional[str] = None, session_id: str = "default"):
        """Stream response with Query Expansion, Deduplication, and Structured Logging."""
        start_time = time.time()
        
        # Manage history before streaming to prevent concurrency issues
        await self._manage_history_size(session_id)
        
        cache_key = f"rag_cache:{session_id}:{question}:{doc_type or 'all'}"
        cached_response = redis_manager.get_cache(cache_key)
        
        if cached_response:
            logger.info(f"Serving from cache: {question}")
            # STREAM CHAR-BY-CHAR (Fix #4)
            for char in cached_response["answer"]:
                yield f"data: {json.dumps({'token': char, 'sources': cached_response['sources']})}\n\n"
                await asyncio.sleep(0.003)
            yield "data: [DONE]\n\n"
            return

        try:
            # 1. QUERY OPTIMIZATION & EXPANSION
            optimized_query = await self._rewrite_query(question)
            expanded_query = await self._expand_query(optimized_query)
            
            # 2. RETRIEVAL (Fix #3: Context Guard k=8 is already in retriever)
            loop = asyncio.get_event_loop()
            docs = await loop.run_in_executor(None, lambda: self.retriever.invoke(expanded_query))
            
            # 3. CONTEXT COMPRESSION & TRIMMING
            filtered_docs = self._deduplicate_docs(docs)
            filtered_docs = filtered_docs[:5]  # Top N Compression
            filtered_docs = self._trim_docs(filtered_docs, max_tokens=settings.max_context_tokens)
            context_text = self._format_docs(filtered_docs)

            logger.info(json.dumps({
                "action": "retrieval_summary",
                "original_docs_count": len(docs),
                "docs_after_dedup_trim": len(filtered_docs),
                "context_length_chars": len(context_text),
                "session_id": session_id
            }))

            # OBSERVABILITY
            latency = time.time() - start_time
            logger.info(json.dumps({
                "action": "stream_query",
                "query": question,
                "optimized_query": optimized_query,
                "expanded_query": expanded_query,
                "docs_retrieved": len(filtered_docs),
                "session_id": session_id,
                "latency_sec": f"{latency:.4f}"
            }))

            sources = []
            seen = set()
            for doc in filtered_docs:
                source_key = f"{doc.metadata.get('source')}_{doc.metadata.get('page')}"
                if source_key not in seen:
                    sources.append({
                        "source": doc.metadata.get('source', 'Unknown'),
                        "page": doc.metadata.get('page', 'N/A'),
                        "content_preview": doc.page_content[:200] + "..."
                    })
                    seen.add(source_key)

            yield f"data: {json.dumps({'sources': sources})}\n\n"

            full_answer = ""
            config = {"configurable": {"session_id": session_id}}

            if settings.debug and question.strip().lower() == "__force_test_response__":
                full_answer = "Test response working"
                logger.info("Force-test mode hit: returning static response")
                yield f"data: {json.dumps({'token': full_answer})}\n\n"
                redis_manager.set_cache(cache_key, {"answer": full_answer, "sources": sources}, expire_seconds=300)
                yield "data: [DONE]\n\n"
                return
            
            # Invoke chain with pre-processed context
            async for chunk in self.chain.astream(
                {"question": question, "context": context_text}, 
                config=config
            ):
                if chunk is not None:
                    text_token = self._extract_text(chunk)
                    full_answer += text_token
                    yield f"data: {json.dumps({'token': text_token})}\n\n"

            logger.info(json.dumps({"action": "llm_output_summary", "output_length_chars": len(full_answer), "session_id": session_id}))

            # Cache the clean string
            redis_manager.set_cache(cache_key, {"answer": full_answer, "sources": sources}, expire_seconds=3600)
            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"Stream error: {e}", exc_info=True)
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            yield "data: [DONE]\n\n"

    def query(self, question: str, session_id: str = "default") -> Dict[str, any]:
        """Sync query wrapper."""
        # For sync, to keep it simple, we run the async history manager synchronously
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(self._manage_history_size(session_id))
        else:
            loop.run_until_complete(self._manage_history_size(session_id))
            
        docs = self.retriever.invoke(question)
        filtered_docs = self._deduplicate_docs(docs)
        filtered_docs = filtered_docs[:5]  # Compression
        filtered_docs = self._trim_docs(filtered_docs, max_tokens=settings.max_context_tokens)
        context_text = self._format_docs(filtered_docs)
        
        logger.info(json.dumps({
            "action": "sync_query",
            "query": question,
            "docs_retrieved": len(filtered_docs),
            "session_id": session_id
        }))
        
        config = {"configurable": {"session_id": session_id}}
        result = self.chain.invoke({"question": question, "context": context_text}, config=config)
        answer = self._extract_text(result)
        return {"answer": answer, "sources": [d.metadata for d in docs], "success": True}
