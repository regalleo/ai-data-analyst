"""
RAG (Retrieval-Augmented Generation) module.
Manages per-user hybrid search indexes for dataset documentation.
"""
from typing import List, Optional, Dict

# In-memory storage for RAG indexes (per-user isolation)
# In production, use Redis with TTL or disk-based storage
_user_rag_store: Dict[int, any] = {}


def build_rag_index(user_id: int, documents: List[str]) -> None:
    """
    Build a hybrid RAG index for a specific user.

    Args:
        user_id: User ID for isolation
        documents: List of document texts to index
    """
    if documents:
        from hybrid_search import HybridSearch
        _user_rag_store[user_id] = HybridSearch(documents)


def query_rag_index(user_id: int, query: str, top_k: int = 5) -> List[str]:
    """
    Query a user's RAG index with hybrid search.
    
    Args:
        user_id: User ID for isolation
        query: Search query
        top_k: Number of results
        
    Returns:
        List of relevant documents
        
    Raises:
        ValueError: If no RAG index exists for user
    """
    hybrid = _user_rag_store.get(user_id)
    
    if hybrid is None:
        raise ValueError(
            f"No RAG index found for user {user_id}. "
            "Please upload and index your datasets first."
        )
    
    return hybrid.search(query, top_k=top_k)


def delete_rag_index(user_id: int) -> bool:
    """
    Delete a user's RAG index (e.g., when deleting all datasets).
    
    Args:
        user_id: User ID
        
    Returns:
        True if index was deleted, False if none existed
    """
    if user_id in _user_rag_store:
        del _user_rag_store[user_id]
        return True
    return False


def get_rag_index_size(user_id: int) -> int:
    """
    Get the number of documents in a user's RAG index.
    
    Args:
        user_id: User ID
        
    Returns:
        Number of documents, 0 if no index
    """
    hybrid = _user_rag_store.get(user_id)
    if hybrid:
        return len(hybrid.documents)
    return 0


def rebuild_rag_index(user_id: int, documents: List[str]) -> None:
    """
    Rebuild a user's RAG index with new documents.
    
    Args:
        user_id: User ID
        documents: New list of document texts
    """
    delete_rag_index(user_id)
    build_rag_index(user_id, documents)

