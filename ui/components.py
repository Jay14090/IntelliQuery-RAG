"""
Reusable UI components for the Gradio interface.

Provides Mermaid-based graph visualisation and formatting helpers.
"""

from __future__ import annotations

# ─── Graph node metadata ────────────────────────────────────────────────
GRAPH_NODES = [
    "anonymize_query",
    "generate_plan",
    "resolve_entities",
    "route_task",
    "retrieve_documents",
    "distill_context",
    "reason_and_answer",
    "verify_grounding",
    "advance_or_replan",
    "synthesize_response",
]

_NODE_LABELS = {
    "anonymize_query": "🔒 Anonymise Query",
    "generate_plan": "📋 Generate Plan",
    "resolve_entities": "🔓 Resolve Entities",
    "route_task": "🔀 Route Task",
    "retrieve_documents": "📚 Retrieve Docs",
    "distill_context": "🧹 Distill Context",
    "reason_and_answer": "🧠 Reason & Answer",
    "verify_grounding": "🔍 Verify Grounding",
    "advance_or_replan": "🔄 Advance / Replan",
    "synthesize_response": "✨ Synthesise Response",
}

_MERMAID_EDGES = [
    ("anonymize_query", "generate_plan"),
    ("generate_plan", "resolve_entities"),
    ("resolve_entities", "route_task"),
    ("route_task", "retrieve_documents"),
    ("route_task", "reason_and_answer"),
    ("retrieve_documents", "distill_context"),
    ("distill_context", "reason_and_answer"),
    ("reason_and_answer", "verify_grounding"),
    ("verify_grounding", "advance_or_replan"),
    ("advance_or_replan", "route_task"),
    ("advance_or_replan", "synthesize_response"),
    ("route_task", "synthesize_response"),
]


def render_mermaid_graph(current_node: str | None = None) -> str:
    """
    Generate a Mermaid flowchart string with the active node highlighted.

    Parameters
    ----------
    current_node : str, optional
        The currently executing node name.  Highlighted in green.

    Returns
    -------
    str
        Complete Mermaid ``graph LR`` definition.
    """
    lines = ["graph LR"]

    # Declare nodes
    for node_id in GRAPH_NODES:
        label = _NODE_LABELS.get(node_id, node_id)
        lines.append(f'    {node_id}["{label}"]')

    # Edges
    for src, dst in _MERMAID_EDGES:
        lines.append(f"    {src} --> {dst}")

    # Styling
    lines.append("")
    lines.append("    %% Styling")
    for node_id in GRAPH_NODES:
        if node_id == current_node:
            lines.append(
                f"    style {node_id} fill:#22c55e,stroke:#15803d,"
                f"color:#fff,stroke-width:3px"
            )
        else:
            lines.append(
                f"    style {node_id} fill:#1e293b,stroke:#475569,"
                f"color:#e2e8f0,stroke-width:1px"
            )

    return "\n".join(lines)


def format_reasoning_trace(trace: list[str]) -> str:
    """
    Format the reasoning trace list into a readable markdown string.

    Parameters
    ----------
    trace : list[str]
        List of reasoning step descriptions.

    Returns
    -------
    str
        Markdown-formatted reasoning chain.
    """
    if not trace:
        return "_No reasoning steps recorded yet._"

    lines = ["### 🧠 Reasoning Trace\n"]
    for i, step in enumerate(trace, start=1):
        lines.append(f"**Step {i}:**\n{step}\n")
        lines.append("---\n")
    return "\n".join(lines)
