from storage.vector_store import VectorStore
from retrieval.bm25 import BM25Retriever
from retrieval.rrf import reciprocal_rank_fusion
from flashrank import Ranker, RerankRequest
import logging

class HybridRetriever:
    def __init__(self):
        self.vector_store = VectorStore()
        self.bm25 = BM25Retriever()
        try:
            self.ranker = Ranker()
        except Exception as e:
            logging.error(f"Failed to load FlashRank: {e}")
            self.ranker = None

    async def retrieve(self, query: str, k: int = 10):
        try:
            # 1. Vector Search
            vector_docs = self.vector_store.search(query, k=k)
            
            # 2. BM25 Search (Needs documents to be indexed first, usually done during ingestion)
            # For simplicity in this demo, if BM25 is empty, we just use vector
            bm25_docs = self.bm25.search(query, k=k)
            
            # 3. Combine with RRF
            if not bm25_docs:
                merged = vector_docs
            else:
                merged = reciprocal_rank_fusion([vector_docs, bm25_docs])
            
            # 4. Rerank with FlashRank
            if self.ranker and merged:
                passages = [
                    {"id": i, "text": d.page_content, "meta": d.metadata} 
                    for i, d in enumerate(merged)
                ]
                rerank_request = RerankRequest(query=query, passages=passages)
                results = self.ranker.rerank(rerank_request)
                
                # Convert back to LangChain documents
                from langchain_core.documents import Document
                reranked_docs = [
                    Document(page_content=r["text"], metadata=r["meta"]) 
                    for r in results[:5]
                ]
                return reranked_docs
                
            return merged[:5]
        except Exception as e:
            logging.error(f"Retrieval error: {str(e)}")
            return []
            
    def update_bm25(self, all_docs):
        self.bm25.index(all_docs)
