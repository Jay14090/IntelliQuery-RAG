"""Document retrieval layer (FAISS-backed)."""

from intelliquery.retrievers.multi_retriever import DocumentRetriever
from intelliquery.retrievers.vector_store import FAISSStoreManager

__all__ = ["FAISSStoreManager", "DocumentRetriever"]
