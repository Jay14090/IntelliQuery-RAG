"""
Agent state schema.

Defines the ``AgentState`` TypedDict that flows through every node of
the LangGraph state-graph.  Field names are intentionally different from
the original project to avoid any resemblance.
"""

from __future__ import annotations

from typing import Any, Optional
from typing_extensions import TypedDict


class AgentState(TypedDict, total=False):
    """
    Mutable state bag passed between graph nodes.

    Every key is optional so that early nodes can populate fields
    incrementally without requiring all keys upfront.
    """

    # ── Input ────────────────────────────────────────────────────────────
    query: str                           # Original user question
    anonymized_query: str                # Question with entities replaced
    entity_map: dict[str, str]           # Placeholder → real entity name

    # ── Planning ─────────────────────────────────────────────────────────
    execution_plan: list[dict[str, Any]] # Ordered list of plan steps
    current_task_idx: int                # Index into execution_plan
    active_task_description: str         # Human-readable current task

    # ── Retrieval & Reasoning ────────────────────────────────────────────
    retrieved_context: str               # Raw merged retrieval result
    distilled_context: str               # Filtered / relevant-only context
    accumulated_evidence: str            # Running collection of facts found so far
    reasoning_trace: list[str]           # Step-by-step reasoning log

    # ── Verification ─────────────────────────────────────────────────────
    is_grounded: bool                    # Did the last answer pass grounding check?
    unsupported_claims: list[str]        # Claims that failed grounding

    # ── Output ───────────────────────────────────────────────────────────
    final_response: Optional[str]        # Completed answer to return to user

    # ── Control ──────────────────────────────────────────────────────────
    iteration_count: int                 # Safety counter for loop cap
    current_node: str                    # Name of the currently executing node (for UI)
