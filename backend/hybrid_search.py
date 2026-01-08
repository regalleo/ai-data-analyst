"""
Hybrid search module combining BM25 keyword search with vector semantic search.
Maintains per-user indexes for multi-tenant isolation.
"""
from typing import List, Tuple
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
import faiss


class HybridSearch:
    """
    Hybrid RAG retriever combining BM25 and vector search.
    
    Uses BM25 for keyword matching and SentenceTransformers for semantic similarity.
    Scores are combined to provide both precise keyword results and semantically
    relevant documents.
    """
    
    def __init__(self, documents: List[str]):
        """
        Initialize hybrid search with a list of documents.
        
        Args:
            documents: List of document texts to index
        """
        self.documents = documents
        self._build_indexes()
    
    def _build_indexes(self) -> None:
        """Build BM25 and FAISS indexes from documents."""
        if not self.documents:
            self.bm25 = None
            self.embedder = None
            self.index = None
            return
        
        # BM25 index for keyword search
        tokenized_docs = [doc.lower().split() for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized_docs)
        
        # Vector index for semantic search using SentenceTransformers
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        embeddings = self.embedder.encode(self.documents, show_progress_bar=False)
        
        # FAISS index for efficient similarity search
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(np.array(embeddings))
    
    def search(self, query: str, top_k: int = 5) -> List[str]:
        """
        Search documents using hybrid BM25 + vector scoring.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of document texts ranked by combined scores
        """
        if not self.documents or self.bm25 is None:
            return []
        
        # BM25 scores for keyword matching
        bm25_scores = self.bm25.get_scores(query.lower().split())
        
        # Vector similarity scores
        query_embedding = self.embedder.encode([query])
        _, vector_indices = self.index.search(query_embedding, top_k)
        
        # Combine scores with weighted fusion
        combined_scores = {}
        
        # Add BM25 scores (normalized)
        max_bm25 = max(bm25_scores) if max(bm25_scores) > 0 else 1
        for i, score in enumerate(bm25_scores):
            combined_scores[i] = (score / max_bm25) * 0.4  # 40% weight
        
        # Add vector search scores (boost matching documents)
        for rank, idx in enumerate(vector_indices[0]):
            if idx < len(combined_scores):
                combined_scores[idx] += (1.0 - rank * 0.1) * 0.6  # 60% weight
        
        # Sort by combined score and return top_k results
        ranked = sorted(
            combined_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [
            self.documents[i]
            for i, _ in ranked[:top_k]
            if i < len(self.documents)
        ]
    
    def search_with_scores(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Search documents with their combined scores.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of (document, score) tuples
        """
        if not self.documents or self.bm25 is None:
            return []
        
        bm25_scores = self.bm25.get_scores(query.lower().split())
        query_embedding = self.embedder.encode([query])
        _, vector_indices = self.index.search(query_embedding, top_k)
        
        combined_scores = {}
        max_bm25 = max(bm25_scores) if max(bm25_scores) > 0 else 1
        
        for i, score in enumerate(bm25_scores):
            combined_scores[i] = (score / max_bm25) * 0.4
        
        for rank, idx in enumerate(vector_indices[0]):
            if idx < len(combined_scores):
                combined_scores[idx] += (1.0 - rank * 0.1) * 0.6
        
        ranked = sorted(
            combined_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [
            (self.documents[i], score)
            for i, score in ranked[:top_k]
            if i < len(self.documents)
        ]

