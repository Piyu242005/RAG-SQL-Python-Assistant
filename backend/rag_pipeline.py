"""RAG pipeline implementation using LangChain."""
from typing import List, Dict, Optional
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory, RedisChatMessageHistory
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough
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
from config import settings

class RAGPipeline:
    """RAG pipeline for question answering."""
    
    def __init__(self):
        """Initialize RAG pipeline."""
        self.vector_store_manager = VectorStoreManager()
        self.ollama_manager = OllamaManager()
        self.llm = None
        self.retriever = None
        self.chain = None
        self.history_store = {} # Session memory
        
        # Initialize components
        self._initialize_llm()
        self._initialize_retriever(use_hybrid=True)
        self._initialize_reranker()
        self._initialize_chain()
    
    def _initialize_llm(self):
        """Initialize Ollama LLM."""
        print(" Initializing Ollama LLM...")
        self.llm = Ollama(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            temperature=0.2,
            num_ctx=2048,
            num_predict=512,
            top_k=30,
            top_p=0.8,
            repeat_penalty=1.1,
        )
        print("[OK] LLM initialized")
    
    def _initialize_retriever(self, use_hybrid: bool = True):
        """Initialize document retriever.
        
        Args:
            use_hybrid: Whether to use hybrid search (Vector + BM25)
        """
        print(f" Initializing {'hybrid ' if use_hybrid else ''}retriever...")
        self.vector_store_manager.initialize_vectorstore()
        
        if use_hybrid:
            self.base_retriever = self.vector_store_manager.get_hybrid_retriever(k=20)
        else:
            self.base_retriever = self.vector_store_manager.get_retriever(
                k=20,
                search_type="mmr"
            )
        
        # Initially, retriever is the base retriever
        self.retriever = self.base_retriever
        print("[OK] Base retriever initialized (k=20 for reranking)")
        
    def _initialize_reranker(self):
        """Initialize FlashRank reranker for better precision."""
        print(" Initializing FlashRank reranker...")
        try:
            compressor = FlashrankRerank(model="ms-marco-MiniLM-L-12-v2", top_n=5)
            self.retriever = ContextualCompressionRetriever(
                base_compressor=compressor, 
                base_retriever=self.base_retriever
            )
            print("[OK] Reranker initialized")
        except Exception as e:
            print(f"[X] Failed to initialize reranker: {str(e)}")
            print("Falling back to base retriever.")
            self.retriever = self.base_retriever
    
    def _initialize_chain(self):
        """Initialize RAG chain."""
        print(" Initializing RAG chain...")
        
        # Create prompt template
        template = """You are an expert SQL and Python assistant. Answer using ONLY the provided reference material. Be concise.

Reference:
{context}

Question: {question}

Rules:
- Start with a direct answer (2-3 sentences)
- Include a code example if relevant (```sql or ```python)
- Use markdown formatting
- Do NOT hallucinate or mention "context"
- If info is insufficient, say so

Answer:"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert SQL and Python assistant."),
            MessagesPlaceholder(variable_name="history"),
            ("human", template)
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
        
        # Wrap with message history using Redis
        def get_session_history(session_id: str):
            return RedisChatMessageHistory(
                session_id=session_id,
                url=settings.redis_url,
                ttl=3600 # 1 hour TTL
            )

        self.chain = RunnableWithMessageHistory(
            self.base_chain,
            get_session_history,
            input_messages_key="question",
            history_messages_key="history",
        )
        
        print("[OK] RAG chain with memory initialized")
    
    def _format_docs(self, docs: List[Document]) -> str:
        """Format retrieved documents for context.
        
        Args:
            docs: List of retrieved documents
            
        Returns:
            Formatted context string
        """
        formatted = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get('source', 'Unknown')
            page = doc.metadata.get('page', 'N/A')
            formatted.append(f"[Source: {source}, Page: {page}]\n{doc.page_content}\n")
        
        return "\n".join(formatted)
    
    def query(self, question: str) -> Dict[str, any]:
        """Query the RAG system.
        
        Args:
            question: User question
            
        Returns:
            Dictionary with answer and source documents
        """
        try:
            # Retrieve relevant documents
            docs = self.retriever.invoke(question)
            
            # Generate answer
            answer = self.chain.invoke(question)
            
            # Format sources
            sources = []
            seen = set()  # Avoid duplicate sources
            
            for doc in docs:
                source_key = f"{doc.metadata.get('source')}_{doc.metadata.get('page')}"
                if source_key not in seen:
                    sources.append({
                        "source": doc.metadata.get('source', 'Unknown'),
                        "page": doc.metadata.get('page', 'N/A'),
                        "content_preview": doc.page_content[:200] + "..."
                    })
                    seen.add(source_key)
            
            return {
                "answer": answer,
                "sources": sources,
                "success": True
            }
        
        except Exception as e:
            raise RuntimeError(f"Error processing query: {str(e)}")
    
    def query_with_filter(self, question: str, doc_type: Optional[str] = None) -> Dict[str, any]:
        """Query with document type filter.
        
        Args:
            question: User question
            doc_type: Filter by document type ('mysql' or 'python')
            
        Returns:
            Dictionary with answer and source documents
        """
        try:
            # Retrieve with filter
            if doc_type:
                docs = self.vector_store_manager.similarity_search(
                    query=question,
                    k=3,
                    filter={"doc_type": doc_type}
                )
            else:
                docs = self.retriever.invoke(question)
            
            # Format context
            context = self._format_docs(docs)
            
            # Generate answer
            answer = self.chain.invoke(question)
            
            # Format sources
            sources = []
            seen = set()
            
            for doc in docs:
                source_key = f"{doc.metadata.get('source')}_{doc.metadata.get('page')}"
                if source_key not in seen:
                    sources.append({
                        "source": doc.metadata.get('source', 'Unknown'),
                        "page": doc.metadata.get('page', 'N/A'),
                        "doc_type": doc.metadata.get('doc_type', 'Unknown'),
                        "content_preview": doc.page_content[:200] + "..."
                    })
                    seen.add(source_key)
            
            return {
                "answer": answer,
                "sources": sources,
                "success": True,
                "filter_applied": doc_type
            }
        
        except Exception as e:
            raise RuntimeError(f"Error processing query: {str(e)}")

    async def stream_query(self, question: str, doc_type: Optional[str] = None, session_id: str = "default"):
        """Stream the RAG response with source documentation."""
        import json
        try:
            # 1. Retrieve relevant documents for sources
            docs = await self.retriever.ainvoke(question)
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
            
            # Send metadata/sources first so UI can display them immediately
            yield f"data: {json.dumps({'sources': sources})}\n\n"

            # 2. Stream the LLM response
            config = {"configurable": {"session_id": session_id}}
            async for chunk in self.chain.astream(question, config=config):
                if chunk:
                    yield f"data: {json.dumps({'token': chunk})}\n\n"
            
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            yield "data: [DONE]\n\n"


# Example usage and testing
if __name__ == "__main__":
    print("=" * 60)
    print(" Testing RAG Pipeline")
    print("=" * 60)
    
    # Initialize pipeline
    rag = RAGPipeline()
    
    # Test queries
    test_queries = [
        "What is a SQL JOIN?",
        "How do I create a Python class?",
        "Explain SELECT statement in SQL"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Question: {query}")
        print(f"{'='*60}")
        
        result = rag.query(query)
        
        if result['success']:
            print(f"\nAnswer:\n{result['answer']}")
            print(f"\nSources:")
            for source in result['sources']:
                print(f"  - {source['source']} (Page {source['page']})")
        else:
            print(f"\nError: {result.get('error', 'Unknown error')}")
