"""
Configuration loader for IntelliQuery-RAG.

Merges settings from:
    1. config.yaml  — non-secret parameters (models, thresholds, paths)
    2. .env         — secret API keys

Exposes a single ``Settings`` dataclass and a ``load_settings()`` factory.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from dotenv import load_dotenv

# ─── Defaults ──────────────────────────────────────────────────────────
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_CONFIG_PATH = _PROJECT_ROOT / "config.yaml"


@dataclass
class LLMSettings:
    """Parameters forwarded to the language-model provider."""
    provider: str = "openai"
    model_name: str = "gpt-4o"
    temperature: float = 0.0
    max_output_tokens: int = 2048
    request_timeout: int = 120


@dataclass
class EmbeddingSettings:
    """Parameters for the embedding model."""
    provider: str = "openai"
    model_name: str = "text-embedding-3-small"


@dataclass
class RetrieverSettings:
    """How many documents each retriever should fetch."""
    chunk_top_k: int = 2
    summary_top_k: int = 2
    quotes_top_k: int = 8


@dataclass
class ProcessingSettings:
    """Text-splitting and chapter detection parameters."""
    chunk_size: int = 1200
    chunk_overlap: int = 150
    chapter_split_pattern: str = r"(BOOK\s\w+.*?)(?=BOOK\s\w+|$)"


@dataclass
class VectorStoreSettings:
    """Where and how to persist FAISS indexes."""
    backend: str = "faiss"
    persist_directory: str = "./data"
    chunks_index: str = "chunks_index"
    summaries_index: str = "summaries_index"
    quotes_index: str = "quotes_index"


@dataclass
class AgentSettings:
    """Behavioural knobs for the reasoning agent."""
    max_iterations: int = 10
    enable_verification: bool = True
    verbose: bool = True


@dataclass
class UISettings:
    """Gradio front-end options."""
    theme: str = "soft"
    server_port: int = 7860
    share: bool = False


@dataclass
class Settings:
    """Top-level configuration container."""

    llm: LLMSettings = field(default_factory=LLMSettings)
    embeddings: EmbeddingSettings = field(default_factory=EmbeddingSettings)
    retriever: RetrieverSettings = field(default_factory=RetrieverSettings)
    processing: ProcessingSettings = field(default_factory=ProcessingSettings)
    vector_store: VectorStoreSettings = field(default_factory=VectorStoreSettings)
    agent: AgentSettings = field(default_factory=AgentSettings)
    ui: UISettings = field(default_factory=UISettings)

    # API keys (populated from .env)
    openai_api_key: str | None = None
    groq_api_key: str | None = None
    anthropic_api_key: str | None = None


def _merge_section(dc_instance, yaml_section: dict) -> None:
    """Overwrite dataclass fields from a YAML dict (ignoring unknown keys)."""
    if not yaml_section:
        return
    for key, value in yaml_section.items():
        if hasattr(dc_instance, key):
            setattr(dc_instance, key, value)


def load_settings(config_path: str | Path | None = None) -> Settings:
    """
    Build a ``Settings`` object by layering config.yaml → .env.

    Parameters
    ----------
    config_path : path-like, optional
        Explicit path to a YAML config file.  Falls back to the project-root
        ``config.yaml``.

    Returns
    -------
    Settings
        Fully-populated configuration dataclass.
    """
    load_dotenv()

    settings = Settings()

    # ── YAML layer ──────────────────────────────────────────────────────
    cfg_file = Path(config_path) if config_path else _DEFAULT_CONFIG_PATH
    if cfg_file.is_file():
        with open(cfg_file, encoding="utf-8") as fh:
            raw = yaml.safe_load(fh) or {}

        _merge_section(settings.llm, raw.get("llm"))
        _merge_section(settings.embeddings, raw.get("embeddings"))
        _merge_section(settings.retriever, raw.get("retriever"))
        _merge_section(settings.processing, raw.get("processing"))
        _merge_section(settings.vector_store, raw.get("vector_store"))
        _merge_section(settings.agent, raw.get("agent"))
        _merge_section(settings.ui, raw.get("ui"))

    # ── Environment layer (secrets) ─────────────────────────────────────
    settings.openai_api_key = os.getenv("OPENAI_API_KEY")
    settings.groq_api_key = os.getenv("GROQ_API_KEY")
    settings.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

    # Push into os.environ so downstream libs (langchain-openai etc.) pick it up
    if settings.openai_api_key:
        os.environ["OPENAI_API_KEY"] = settings.openai_api_key

    return settings
