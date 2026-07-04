"""
LangGraph state-graph builder.

Assembles the deterministic reasoning graph from the node functions
defined in :mod:`intelliquery.agents.nodes`.

Graph topology::

    anonymize_query → generate_plan → resolve_entities
         ↓
    route_task ──[RETRIEVE]──→ retrieve_documents → distill_context → reason_and_answer
         │                                                                  ↓
         └──[REASON]──→ reason_and_answer ──→ verify_grounding → advance_or_replan
                                                                       ↓          ↓
                                                              route_task    synthesize_response
                                                            (loop back)        (END)
"""

from __future__ import annotations

from typing import Any

from langgraph.graph import END, StateGraph

from intelliquery.agents.state import AgentState
from intelliquery.agents.nodes import create_node_functions
from intelliquery.chains import (
    AnonymizeChain,
    DistillChain,
    PlanChain,
    ReasonChain,
    VerifyChain,
)
from intelliquery.config import Settings
from intelliquery.providers.openai_provider import OpenAILLMProvider
from intelliquery.retrievers.multi_retriever import DocumentRetriever
from intelliquery.retrievers.vector_store import FAISSStoreManager


# ─── Routing helpers ─────────────────────────────────────────────────────

def _route_after_task(state: AgentState) -> str:
    """Decide whether the current task is a RETRIEVE or REASON action."""
    plan = state.get("execution_plan", [])
    idx = state.get("current_task_idx", 0)
    if idx >= len(plan):
        return "synthesize_response"
    action = plan[idx].get("action", "RETRIEVE")
    return "retrieve_documents" if action == "RETRIEVE" else "reason_and_answer"


def _should_continue(state: AgentState) -> str:
    """After advancing, check whether we're done or should loop."""
    plan = state.get("execution_plan", [])
    idx = state.get("current_task_idx", 0)
    max_iter = 10  # safety cap
    if idx >= len(plan) or state.get("iteration_count", 0) >= max_iter:
        return "synthesize_response"
    return "route_task"


# ─── Public builder ──────────────────────────────────────────────────────

def build_agent_graph(
    settings: Settings | None = None,
    retriever: DocumentRetriever | None = None,
) -> StateGraph:
    """
    Construct the full agent graph ready for ``.compile().invoke()``.

    Parameters
    ----------
    settings : Settings, optional
        Loaded configuration.  Uses defaults if not supplied.
    retriever : DocumentRetriever, optional
        Pre-built retriever.  If not supplied, one is constructed from
        ``settings``.

    Returns
    -------
    StateGraph
        Compiled LangGraph application.
    """
    if settings is None:
        from intelliquery.config import load_settings
        settings = load_settings()

    # ── Provider ──────────────────────────────────────────────────────
    provider = OpenAILLMProvider()
    llm = provider.build_chat_model(
        model_name=settings.llm.model_name,
        temperature=settings.llm.temperature,
        max_tokens=settings.llm.max_output_tokens,
    )
    embeddings = provider.build_embeddings(model_name=settings.embeddings.model_name)

    # ── Retriever ─────────────────────────────────────────────────────
    if retriever is None:
        store_mgr = FAISSStoreManager(
            embeddings=embeddings,
            persist_dir=settings.vector_store.persist_directory,
        )
        retriever = DocumentRetriever(
            store_manager=store_mgr,
            chunks_index=settings.vector_store.chunks_index,
            summaries_index=settings.vector_store.summaries_index,
            quotes_index=settings.vector_store.quotes_index,
            chunk_k=settings.retriever.chunk_top_k,
            summary_k=settings.retriever.summary_top_k,
            quotes_k=settings.retriever.quotes_top_k,
        )

    # ── Chains ────────────────────────────────────────────────────────
    anonymize_chain = AnonymizeChain(llm)
    plan_chain = PlanChain(llm)
    distill_chain = DistillChain(llm)
    reason_chain = ReasonChain(llm)
    verify_chain = VerifyChain(llm)

    # ── Node functions ────────────────────────────────────────────────
    nodes = create_node_functions(
        anonymize_chain=anonymize_chain,
        plan_chain=plan_chain,
        distill_chain=distill_chain,
        reason_chain=reason_chain,
        verify_chain=verify_chain,
        retriever=retriever,
        verbose=settings.agent.verbose,
    )

    # ── Graph wiring ──────────────────────────────────────────────────
    graph = StateGraph(AgentState)

    # Add nodes
    for name, fn in nodes.items():
        graph.add_node(name, fn)

    # Entry point
    graph.set_entry_point("anonymize_query")

    # Linear edges (beginning of pipeline)
    graph.add_edge("anonymize_query", "generate_plan")
    graph.add_edge("generate_plan", "resolve_entities")
    graph.add_edge("resolve_entities", "route_task")

    # Conditional: route_task decides RETRIEVE vs REASON (or done)
    graph.add_conditional_edges(
        "route_task",
        _route_after_task,
        {
            "retrieve_documents": "retrieve_documents",
            "reason_and_answer": "reason_and_answer",
            "synthesize_response": "synthesize_response",
        },
    )

    # Retrieval sub-pipeline
    graph.add_edge("retrieve_documents", "distill_context")
    graph.add_edge("distill_context", "reason_and_answer")

    # After reasoning → verify → advance
    graph.add_edge("reason_and_answer", "verify_grounding")
    graph.add_edge("verify_grounding", "advance_or_replan")

    # Conditional: loop back or synthesize
    graph.add_conditional_edges(
        "advance_or_replan",
        _should_continue,
        {
            "route_task": "route_task",
            "synthesize_response": "synthesize_response",
        },
    )

    # Terminal
    graph.add_edge("synthesize_response", END)

    return graph.compile()
