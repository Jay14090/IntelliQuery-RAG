"""
FAISS vector store management.

Provides :class:`FAISSStoreManager` — a thin wrapper around LangChain's FAISS
integration that handles building, saving, and loading indexes.
"""

from __future__ import annotations

from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


class FAISSStoreManager:
    """
    Create, persist, and load FAISS indexes.

    Parameters
    ----------
    embeddings : Embeddings
        Embedding model used for encoding.
    persist_dir : str | Path
        Root directory where indexes are saved as sub-folders.
    """

    def __init__(self, embeddings: Embeddings, persist_dir: str | Path = "./data") -> None:
        self._embeddings = embeddings
        self._persist_dir = Path(persist_dir)
        self._persist_dir.mkdir(parents=True, exist_ok=True)

    # ── Build ────────────────────────────────────────────────────────────

    def build_from_documents(
        self,
        documents: list[Document],
        index_name: str,
        *,
        chunk_size: int = 1200,
        chunk_overlap: int = 150,
        split: bool = True,
    ) -> FAISS:
        """
        Build a FAISS index from a list of ``Document`` objects.

        If ``split=True`` the documents are chunked with
        ``RecursiveCharacterTextSplitter`` first; set ``split=False`` for
        pre-chunked data (e.g., summaries or quotes).

        The index is automatically saved to ``persist_dir/index_name``.
        """
        if split:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
            )
            docs = splitter.split_documents(documents)
        else:
            docs = documents

        store = FAISS.from_documents(docs, self._embeddings)
        self._save(store, index_name)
        return store

    # ── Persist / Load ───────────────────────────────────────────────────

    def _save(self, store: FAISS, index_name: str) -> None:
        save_path = str(self._persist_dir / index_name)
        store.save_local(save_path)

    def load(self, index_name: str) -> FAISS | None:
        """
        Load a previously persisted FAISS index.

        Returns ``None`` if the index directory does not exist.
        """
        index_path = self._persist_dir / index_name
        if not index_path.exists():
            return None
        return FAISS.load_local(
            str(index_path),
            self._embeddings,
            allow_dangerous_deserialization=True,
        )

    def index_exists(self, index_name: str) -> bool:
        """Check whether an index has been persisted."""
        return (self._persist_dir / index_name).exists()
