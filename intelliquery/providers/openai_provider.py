"""
OpenAI provider — default LLM backend for IntelliQuery-RAG.

Wraps ``langchain-openai`` behind the :class:`LLMProvider` interface so
the rest of the codebase never imports vendor-specific classes directly.
"""

from __future__ import annotations

from typing import Any

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from intelliquery.providers.base import LLMProvider


class OpenAILLMProvider(LLMProvider):
    """Concrete provider backed by OpenAI's API (GPT-4o, etc.)."""

    def build_chat_model(
        self,
        model_name: str = "gpt-4o",
        temperature: float = 0.0,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> ChatOpenAI:
        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

    def build_embeddings(
        self,
        model_name: str = "text-embedding-3-small",
        **kwargs: Any,
    ) -> OpenAIEmbeddings:
        return OpenAIEmbeddings(model=model_name, **kwargs)
