"""RAG pipeline implementation with Redis and optimized retrieval."""
import asyncio
import logging
import json
from typing import List, Dict, Optional
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
            temperature=0.1,  # Lower for more factual answers
            num_ctx=4096,     # Increased context window
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
            # Retrieve 20 candidates for reranking
            self.base_retriever = self.vector_store_manager.get_hybrid_retriever(k=20)
        else:
            self.base_retriever = self.vector_store_manager.get_retriever(k=20, search_type="mmr")
        
        self.retriever = self.base_retriever
    
    def _initialize_reranker(self):
        """Initialize FlashRank reranker (Select top 5)."""
        logger.info("Initializing FlashRank reranker...")
        try:
            # Top 5 final results after reranking 20 candidates
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
        
        # Create RAG chain
        self.base_chain = (
            {
                "context": self.retriever | self._format_docs,
                "question": RunnablePassthrough(),
                "history": lambda x: x.get("history", [])
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        def get_session_history(session_id: str):
            """Get Redis-backed or in-memory history."""
            if redis_manager.client:
                return RedisChatMessageHistory(
                    session_id=f"chat_history:{session_id}",
                    url=settings.redis_url
                )
            if session_id not in self.in_memory_history:
                self.in_memory_history[session_id] = ChatMessageHistory()
            return self.in_memory_history[session_id]

        self.chain = RunnableWithMessageHistory(
            self.base_chain,
            get_session_history,
            input_messages_key="question",
            history_messages_key="history",
        )
        
        logger.info("[OK] RAG chain with persistent history initialized")
    
    def _format_docs(self, docs: List[Document]) -> str:
        """Format retrieved documents with metadata."""
        formatted = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get('source', 'Unknown')
            page = doc.metadata.get('page', 'N/A')
            formatted.append(f"--- Document {i} (Source: {source}, Page: {page}) ---\n{doc.page_content}\n")
        return "\n".join(formatted)
    
    async def stream_query(self, question: str, doc_type: Optional[str] = None, session_id: str = "default"):
        """Stream response with Redis caching."""
        # 1. Check Cache
        cache_key = f"rag_cache:{question}:{doc_type or 'all'}"
        cached_response = redis_manager.get_cache(cache_key)
        
        if cached_response and isinstance(cached_response.get('answer'), str):
            logger.info(f"Serving from cache: {question}")
            yield f"data: {json.dumps({'sources': cached_response['sources']})}\n\n"
            # Split by whitespace to simulate streaming tokens
            tokens = cached_response['answer'].split(' ')
            for i, token in enumerate(tokens):
                # Add space back except for the last token
                t = token + (' ' if i < len(tokens) - 1 else '')
                yield f"data: {json.dumps({'token': t})}\n\n"
                await asyncio.sleep(0.01)
            yield "data: [DONE]\n\n"
            return

        try:
            # 2. Retrieve docs
            loop = asyncio.get_event_loop()
            docs = await loop.run_in_executor(None, lambda: self.retriever.invoke(question))

            sources = []
            seen = set()
            for doc in docs:
                source_key = f"{doc.metadata.get('source')}_{doc.metadata.get('page')}"
                if source_key not in seen:
                    sources.append({
                        "source": doc.metadata.get('source', 'Unknown'),
                        "page": doc.metadata.get('page', 'N/A'),
                        "content_preview": doc.page_content[:200] + "..."
                    })
                    seen.add(source_key)

            # 3. Stream and Capture for Caching
            yield f"data: {json.dumps({'sources': sources})}\n\n"

            full_answer = ""
            config = {"configurable": {"session_id": session_id}}
            
            # Use astream on the base_chain to ensure StrOutputParser works correctly
            # RunnableWithMessageHistory sometimes wraps chunks in metadata
            async for chunk in self.chain.astream({"question": question}, config=config):
                if chunk:
                    # Defensive: ensure chunk is a string
                    text_chunk = str(chunk) if not isinstance(chunk, str) else chunk
                    full_answer += text_chunk
                    yield f"data: {json.dumps({'token': text_chunk})}\n\n"

            # 4. Save to Cache (Expire in 1 hour)
            redis_manager.set_cache(cache_key, {"answer": full_answer, "sources": sources}, expire_seconds=3600)
            
            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"Stream error: {e}", exc_info=True)
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            yield "data: [DONE]\n\n"

    def query(self, question: str, session_id: str = "default") -> Dict[str, any]:
        """Sync query wrapper (not used by frontend but good for testing)."""
        config = {"configurable": {"session_id": session_id}}
        answer = self.chain.invoke({"question": question}, config=config)
        docs = self.retriever.invoke(question)
        return {"answer": answer, "sources": [d.metadata for d in docs], "success": True}
