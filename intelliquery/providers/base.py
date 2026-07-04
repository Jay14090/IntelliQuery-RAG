"""
Abstract base class for LLM providers.

Any new provider (Anthropic, Gemini, Groq, local Ollama) should subclass
``LLMProvider`` and implement :meth:`build_chat_model` and
:meth:`build_embeddings`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings


class LLMProvider(ABC):
    """
    Unified interface that the rest of IntelliQuery-RAG codes against.

    Subclasses must provide concrete LangChain-compatible model instances.
    """

    @abstractmethod
    def build_chat_model(
        self,
        model_name: str,
        temperature: float = 0.0,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> BaseChatModel:
        """Return a LangChain chat model ready for ``.invoke()``."""

    @abstractmethod
    def build_embeddings(self, model_name: str, **kwargs: Any) -> Embeddings:
        """Return a LangChain embeddings instance."""
