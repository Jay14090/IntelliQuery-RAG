"""
Multi-source document retriever.

Combines results from **three** FAISS indexes (chunks, summaries, quotes)
into a single merged context string — the same conceptual approach as the
original but behind a clean OOP interface with configurable k-values.
"""

from __future__ import annotations

from dataclasses import dataclass

from intelliquery.processing.text_cleaner import sanitize_quotes
from intelliquery.retrievers.vector_store import FAISSStoreManager


@dataclass
class RetrievalResult:
    """Structured result of a multi-source retrieval pass."""
    chunks_text: str
    summaries_text: str
    quotes_text: str

    @property
    def merged(self) -> str:
        """All three sources joined with clear delimiters."""
        parts = []
        if self.chunks_text:
            parts.append(f"[Retrieved Chunks]\n{self.chunks_text}")
        if self.summaries_text:
            parts.append(f"[Section Summaries]\n{self.summaries_text}")
        if self.quotes_text:
            parts.append(f"[Book Quotes]\n{self.quotes_text}")
        return "\n\n".join(parts)


class DocumentRetriever:
    """
    Retrieve relevant documents from all three vector stores for a given
    query.

    Parameters
    ----------
    store_manager : FAISSStoreManager
        Handles index loading.
    chunks_index : str
        Name of the chunks FAISS index.
    summaries_index : str
        Name of the summaries FAISS index.
    quotes_index : str
        Name of the quotes FAISS index.
    chunk_k : int
        Number of chunk results to fetch.
    summary_k : int
        Number of summary results to fetch.
    quotes_k : int
        Number of quote results to fetch.
    """

    def __init__(
        self,
        store_manager: FAISSStoreManager,
        chunks_index: str = "chunks_index",
        summaries_index: str = "summaries_index",
        quotes_index: str = "quotes_index",
        chunk_k: int = 2,
        summary_k: int = 2,
        quotes_k: int = 8,
    ) -> None:
        self._manager = store_manager
        self._chunks_index = chunks_index
        self._summaries_index = summaries_index
        self._quotes_index = quotes_index
        self._chunk_k = chunk_k
        self._summary_k = summary_k
        self._quotes_k = quotes_k

        # Lazy-loaded FAISS retriever instances
        self._chunks_retriever = None
        self._summaries_retriever = None
        self._quotes_retriever = None

    # ── Initialisation ───────────────────────────────────────────────────

    def _ensure_loaded(self) -> None:
        """Load indexes on first use (fail-fast if missing)."""
        if self._chunks_retriever is not None:
            return

        chunks_store = self._manager.load(self._chunks_index)
        summaries_store = self._manager.load(self._summaries_index)
        quotes_store = self._manager.load(self._quotes_index)

        if chunks_store is None:
            raise FileNotFoundError(
                f"Chunks index '{self._chunks_index}' not found. "
                "Run the ingestion notebook first."
            )

        self._chunks_retriever = chunks_store.as_retriever(
            search_kwargs={"k": self._chunk_k}
        )
        if summaries_store:
            self._summaries_retriever = summaries_store.as_retriever(
                search_kwargs={"k": self._summary_k}
            )
        if quotes_store:
            self._quotes_retriever = quotes_store.as_retriever(
                search_kwargs={"k": self._quotes_k}
            )

    # ── Public API ───────────────────────────────────────────────────────

    def retrieve(self, query: str, *, verbose: bool = False) -> RetrievalResult:
        """
        Fetch relevant documents from all available stores.

        Parameters
        ----------
        query : str
            The search query.
        verbose : bool
            Print status messages.

        Returns
        -------
        RetrievalResult
        """
        self._ensure_loaded()

        # Chunks
        if verbose:
            print("  🔍 Retrieving relevant text chunks…")
        chunk_docs = self._chunks_retriever.invoke(query)
        chunks_text = " ".join(d.page_content for d in chunk_docs)

        # Summaries
        summaries_text = ""
        if self._summaries_retriever:
            if verbose:
                print("  📑 Retrieving section summaries…")
            sum_docs = self._summaries_retriever.invoke(query)
            summaries_text = " ".join(
                f"{d.page_content} (Section {d.metadata.get('section', '?')})"
                for d in sum_docs
            )

        # Quotes
        quotes_text = ""
        if self._quotes_retriever:
            if verbose:
                print("  💬 Retrieving book quotes…")
            quote_docs = self._quotes_retriever.invoke(query)
            quotes_text = " ".join(d.page_content for d in quote_docs)

        return RetrievalResult(
            chunks_text=sanitize_quotes(chunks_text),
            summaries_text=sanitize_quotes(summaries_text),
            quotes_text=sanitize_quotes(quotes_text),
        )
