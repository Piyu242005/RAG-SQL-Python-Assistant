"""RAG pipeline implementation using LangChain."""
from typing import List, Dict, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import OllamaLLM as Ollama
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
        
        # Initialize components
        self._initialize_llm()
        self._initialize_retriever()
        self._initialize_chain()
    
    def _initialize_llm(self):
        """Initialize Ollama LLM."""
        print(" Initializing Ollama LLM...")
        self.llm = Ollama(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            temperature=0.2,
            num_ctx=4096,
        )
        print("[OK] LLM initialized")
    
    def _initialize_retriever(self):
        """Initialize document retriever."""
        print(" Initializing retriever...")
        self.vector_store_manager.initialize_vectorstore()
        self.retriever = self.vector_store_manager.get_retriever(
            k=5,
            search_type="mmr"
        )
        print("[OK] Retriever initialized")
    
    def _initialize_chain(self):
        """Initialize RAG chain."""
        print(" Initializing RAG chain...")
        
        # Create prompt template
        template = """You are an expert SQL and Python programming assistant.

Use ONLY the provided reference material to answer the user's question.

Reference material:
{context}

Question: {question}

Response rules:
1. Start with a clear, direct answer in 2-4 sentences.
2. If code is relevant, provide a clean, runnable code example with proper syntax highlighting (use ```sql or ```python).
3. Add a brief explanation after the code if needed.
4. Keep the response concise, well-structured, and easy to scan.
5. Use markdown formatting: headers, bold, bullet points.
6. Do NOT use the word "context" or refer to "the provided text".
7. If the information is insufficient, say: "The available documentation does not cover this topic in sufficient detail."
8. Do NOT hallucinate or make up information not present in the reference material.

Answer:"""
        
        prompt = ChatPromptTemplate.from_template(template)
        
        # Create RAG chain using LCEL (LangChain Expression Language)
        self.chain = (
            {
                "context": self.retriever | self._format_docs,
                "question": RunnablePassthrough()
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        print("[OK] RAG chain initialized")
    
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
            return {
                "answer": f"Error processing query: {str(e)}",
                "sources": [],
                "success": False,
                "error": str(e)
            }
    
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
                    k=5,
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
            return {
                "answer": f"Error processing query: {str(e)}",
                "sources": [],
                "success": False,
                "error": str(e)
            }


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
