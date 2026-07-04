"""
IntelliQuery-RAG — Intelligent Graph-Orchestrated RAG Agent
===========================================================

A production-grade Retrieval-Augmented Generation system that uses a
deterministic state-graph to orchestrate complex multi-step question
answering over document corpora.

Modules:
    agents      — LangGraph state-graph and node definitions
    chains      — LLM chain compositions (anonymize, plan, distill, reason, verify)
    processing  — PDF loading, text cleaning, summarization
    prompts     — Versioned prompt templates
    providers   — Abstract LLM provider interface
    retrievers  — FAISS-backed document retrieval
    evaluation  — Ragas-based quality metrics
"""

__version__ = "0.1.0"
__author__ = "jay14"
