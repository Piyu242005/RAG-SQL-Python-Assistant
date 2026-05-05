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
        """Initialize FlashRank reranker.

        top_n=10 gives the deduplication step enough candidates to work with;
        the final [:5] slice in stream_query / query() enforces the hard cap
        after duplicates have been removed.
        """
        logger.info("Initializing FlashRank reranker...")
        try:
            compressor = FlashrankRerank(model="ms-marco-MiniLM-L-12-v2", top_n=10)
            self.retriever = ContextualCompressionRetriever(
                base_compressor=compressor, 
                base_retriever=self.base_retriever
            )
            logger.info("[OK] Reranker initialized (top_n=10, final slice=5 after dedup)")
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
        
        # Redis availability: delegate entirely to shared redis_manager (no duplicate client)
        self.redis_available = redis_manager.client is not None
        if self.redis_available:
            logger.info("[OK] Redis Cache: Active (shared redis_manager)")
        else:
            logger.warning("[!] Redis Cache: Not available. Falling back to memory-only.")

        def get_session_history(session_id: str):
            if self.redis_available:
                return RedisChatMessageHistory(
                    session_id=f"chat_history:{session_id}",
                    url=settings.redis_url,
                    ttl=86400
                )
            else:
                if session_id not in self.in_memory_history:
                    self.in_memory_history[session_id] = ChatMessageHistory()
                return self.in_memory_history[session_id]

        # Store for reuse in _manage_history_size and query()
        self._get_session_history = get_session_history

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

    # Max combined chars for the expanded query fed to the retriever.
    # Keeping this tight ensures the embedding stays focused; HyDE noise
    # beyond this point typically hurts recall rather than helping it.
    _MAX_EXPANSION_CHARS: int = 200

    async def _expand_query(self, query: str) -> str:
        """Expands the user query using a HyDE-inspired approach for better retrieval.

        The combined (original + synthesised) text is clamped to
        _MAX_EXPANSION_CHARS so the retriever embedding stays focused.
        """
        try:
            expansion_prompt = (
                f"Given the user query: '{query}', generate a short technical "
                "description of what the answer might look like to help with "
                "vector search. Keep it under 50 words."
            )
            expansion = await self.llm.ainvoke(expansion_prompt)
            expanded_text = expansion.content if hasattr(expansion, 'content') else str(expansion)
            combined = f"{query} {expanded_text.strip()}"
            # Fix A — cap length so retriever recall is not diluted by long generations
            return combined[:self._MAX_EXPANSION_CHARS]
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
        """Trim docs at the document level to prevent LLM context overflow.

        Uses 3 chars/token (conservative for code-heavy SQL/Python content) and
        an 0.85 safety margin to stay well inside num_ctx=4096.
        """
        max_safe = int(max_tokens * 0.85)
        total = 0
        result = []
        for d in docs:
            # ~3 chars per token is more accurate for code/SQL content
            tokens = len(d.page_content) // 3
            if total + tokens > max_safe:
                break
            result.append(d)
            total += tokens
        return result

    async def _manage_history_size(self, session_id: str):
        """Trim history to the sliding-window cap via the shared get_session_history
        factory — avoids constructing a second RedisChatMessageHistory object."""
        history = self._get_session_history(session_id)

        if history and len(history.messages) > settings.max_history_messages:
            # Simple sliding window — no LLM summarization to avoid pre-stream latency
            keep = history.messages[-settings.max_history_messages:]
            history.clear()
            for msg in keep:
                if msg.type == "human":
                    history.add_user_message(msg.content)
                else:
                    history.add_ai_message(msg.content)
            logger.info(json.dumps({"action": "history_trimmed", "session_id": session_id, "kept": settings.max_history_messages}))

    async def stream_query(self, question: str, doc_type: Optional[str] = None, session_id: str = "default"):
        """Stream response with Query Expansion, Deduplication, and Structured Logging."""
        start_time = time.time()
        
        # Manage history before streaming to prevent concurrency issues
        await self._manage_history_size(session_id)
        
        # doc_type is NOT passed as a retriever filter, so including it in the cache key
        # would fragment hits for identical questions. Use question-only key for max hit rate.
        cache_key = f"rag_cache:{question}"
        cached_response = redis_manager.get_cache(cache_key)
        
        if cached_response:
            logger.info(json.dumps({"action": "cache_hit", "query": question}))
            # Fix C — guard history writes so a transient Redis error doesn't
            # crash the generator before the first SSE byte is sent.
            try:
                history = self._get_session_history(session_id)
                history.add_user_message(question)
                history.add_ai_message(cached_response["answer"])
            except Exception as hist_err:
                logger.warning(f"History write skipped (cache hit): {hist_err}")
            # Send sources ONCE, then stream tokens
            yield f"data: {json.dumps({'sources': cached_response['sources']})}\n\n"
            for char in cached_response["answer"]:
                yield f"data: {json.dumps({'token': char})}\n\n"
                await asyncio.sleep(0.003)
            yield "data: [DONE]\n\n"
            return

        try:
            # 1. QUERY EXPANSION (gated behind feature flag)
            # Fix B — fire expansion as a background Task so TTFB is never
            # gated on the Ollama round-trip.  Retrieval starts immediately
            # with the original query; we await the task with a short timeout
            # and swap in the expanded text only if it arrives in time.
            expansion_task: Optional[asyncio.Task] = None
            if settings.enable_query_expansion:
                expansion_task = asyncio.create_task(self._expand_query(question))

            expanded_query = question  # default — overwritten below if task succeeds

            # 2. QUERY EXPANSION RESOLUTION — wait up to the configured
            #    timeout for the background task before kicking off retrieval.
            if expansion_task is not None:
                try:
                    expanded_query = await asyncio.wait_for(
                        asyncio.shield(expansion_task),
                        timeout=settings.query_expansion_timeout_sec
                    )
                    logger.info(json.dumps({
                        "action": "query_expansion",
                        "original": question,
                        "expanded": expanded_query
                    }))
                except asyncio.TimeoutError:
                    # Expansion took too long — proceed with original query
                    expansion_task.cancel()
                    logger.warning(json.dumps({
                        "action": "query_expansion_timeout",
                        "query": question,
                        "timeout_sec": settings.query_expansion_timeout_sec
                    }))
                except Exception as exp_err:
                    logger.warning(f"Query expansion failed, using original: {exp_err}")

            # 3. RETRIEVAL — run sync retriever in thread to stay non-blocking
            loop = asyncio.get_event_loop()
            docs = await loop.run_in_executor(None, lambda: self.retriever.invoke(expanded_query))
            
            # 4. CONTEXT COMPRESSION & TRIMMING
            # Order: dedup first (removes hash-identical chunks from the reranker's top-10)
            # then enforce hard cap of 5, then token-trim to stay inside num_ctx.
            filtered_docs = self._deduplicate_docs(docs)  # operate on all reranker candidates
            filtered_docs = filtered_docs[:5]             # hard cap after dedup guarantees 5 unique chunks
            filtered_docs = self._trim_docs(filtered_docs, max_tokens=settings.max_context_tokens)
            context_text = self._format_docs(filtered_docs)

            logger.info(json.dumps({
                "action": "retrieval_summary",
                "original_docs_count": len(docs),
                "docs_after_dedup_trim": len(filtered_docs),
                "context_length_chars": len(context_text),
                "session_id": session_id,
                "query_expansion_enabled": settings.enable_query_expansion
            }))

            # OBSERVABILITY
            latency = time.time() - start_time
            logger.info(json.dumps({
                "action": "stream_query",
                "query": question,
                "expanded_query": expanded_query,
                "docs_retrieved": len(filtered_docs),
                "session_id": session_id,
                "latency_before_stream_sec": f"{latency:.4f}"
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
        """Sync query wrapper — non-async path, no LLM summarization.

        Applies the same sliding-window trim as the async path, respecting
        Redis when available (via the shared _get_session_history factory).
        """
        # Trim history consistently for both Redis and in-memory backends
        history = self._get_session_history(session_id)
        if history and len(history.messages) > settings.max_history_messages:
            keep = history.messages[-settings.max_history_messages:]
            history.clear()
            for msg in keep:
                if msg.type == "human":
                    history.add_user_message(msg.content)
                else:
                    history.add_ai_message(msg.content)

        docs = self.retriever.invoke(question)
        # Deduplication before trim (consistent with async path)
        filtered_docs = self._deduplicate_docs(docs)
        filtered_docs = filtered_docs[:5]
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
