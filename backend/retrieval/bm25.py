from rank_bm25 import BM25Okapi
import numpy as np

class BM25Retriever:
    def __init__(self):
        self.bm25 = None
        self.documents = []

    def index(self, documents):
        self.documents = documents
        tokenized_corpus = [doc.page_content.lower().split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def search(self, query: str, k: int = 5):
        if not self.bm25:
            return []
        
        tokenized_query = query.lower().split()
        doc_scores = self.bm25.get_scores(tokenized_query)
        top_n = np.argsort(doc_scores)[::-1][:k]
        
        return [self.documents[i] for i in top_n]
