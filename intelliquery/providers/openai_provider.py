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
    """Concrete provider backed by OpenAI's API (GPT-5, etc.)."""

    def build_chat_model(
        self,
        model_name: str = "gpt-5",
        temperature: float = 0.0,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> ChatOpenAI:
        if model_name.startswith("gpt-5"):
            # GPT-5 models only accept the default temperature and use
            # ``max_completion_tokens`` instead of ``max_tokens``.
            return ChatOpenAI(
                model=model_name,
                max_completion_tokens=max_tokens,
                **kwargs,
            )
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
