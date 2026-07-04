"""Document retrieval layer (FAISS-backed)."""

from intelliquery.retrievers.vector_store import FAISSStoreManager
from intelliquery.retrievers.multi_retriever import DocumentRetriever

__all__ = ["FAISSStoreManager", "DocumentRetriever"]
