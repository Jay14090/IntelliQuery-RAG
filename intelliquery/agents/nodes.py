"""
Individual graph-node functions.

Each function receives and returns an ``AgentState`` dict — LangGraph
handles the merging.  Every node is a standalone, testable unit.
"""

from __future__ import annotations

from typing import Any

from intelliquery.agents.state import AgentState
from intelliquery.chains.anonymizer import AnonymizeChain
from intelliquery.chains.distiller import DistillChain
from intelliquery.chains.planner import PlanChain
from intelliquery.chains.reasoner import ReasonChain
from intelliquery.chains.verifier import VerifyChain
from intelliquery.retrievers.multi_retriever import DocumentRetriever

# ─── Factory ─────────────────────────────────────────────────────────────
# Chains and retriever are injected once at graph-build time and closed
# over by the node functions via ``create_node_functions()``.

def create_node_functions(
    anonymize_chain: AnonymizeChain,
    plan_chain: PlanChain,
    distill_chain: DistillChain,
    reason_chain: ReasonChain,
    verify_chain: VerifyChain,
    retriever: DocumentRetriever,
    *,
    verbose: bool = True,
) -> dict[str, Any]:
    """
    Build all graph-node callables with their dependencies injected.

    Returns a dict keyed by node name → callable(AgentState) → AgentState.
    """

    # ── 1. Anonymise the user's question ─────────────────────────────────
    def anonymize_query(state: AgentState) -> AgentState:
        if verbose:
            print("\n🔒 Node: anonymize_query")
        result = anonymize_chain.run(state["query"])
        if verbose:
            print(f"   Anonymised → {result.anonymized_question}")
            print(f"   Entity map → {result.entity_map}")
        return {
            "anonymized_query": result.anonymized_question,
            "entity_map": result.entity_map,
            "current_node": "anonymize_query",
        }

    # ── 2. Generate execution plan ───────────────────────────────────────
    def generate_plan(state: AgentState) -> AgentState:
        if verbose:
            print("\n📋 Node: generate_plan")
        plan_result = plan_chain.run(state["anonymized_query"])
        steps = [s.model_dump() for s in plan_result.steps]
        if verbose:
            for s in steps:
                print(f"   Step {s['step']}: [{s['action']}] {s['description']}")
        return {
            "execution_plan": steps,
            "current_task_idx": 0,
            "iteration_count": 0,
            "accumulated_evidence": "",
            "reasoning_trace": [],
            "current_node": "generate_plan",
        }

    # ── 3. De-anonymise the plan (resolve entity placeholders) ───────────
    def resolve_entities(state: AgentState) -> AgentState:
        if verbose:
            print("\n🔓 Node: resolve_entities")
        entity_map = state.get("entity_map", {})
        resolved_plan = []
        for step in state["execution_plan"]:
            desc = step["description"]
            for placeholder, real_name in entity_map.items():
                desc = desc.replace(placeholder, real_name)
            resolved_plan.append({**step, "description": desc})
            if verbose:
                print(f"   Step {step['step']}: {desc}")
        return {
            "execution_plan": resolved_plan,
            "current_node": "resolve_entities",
        }

    # ── 4. Route the current task ────────────────────────────────────────
    def route_task(state: AgentState) -> AgentState:
        idx = state.get("current_task_idx", 0)
        plan = state.get("execution_plan", [])
        if idx >= len(plan):
            if verbose:
                print("\n✅ Node: route_task → all tasks complete")
            return {
                "active_task_description": "__DONE__",
                "current_node": "route_task",
            }
        task = plan[idx]
        if verbose:
            print(f"\n🔀 Node: route_task → Step {task['step']}: "
                  f"[{task['action']}] {task['description']}")
        return {
            "active_task_description": task["description"],
            "current_node": "route_task",
        }

    # ── 5. Retrieve documents ────────────────────────────────────────────
    def retrieve_documents(state: AgentState) -> AgentState:
        if verbose:
            print("\n📚 Node: retrieve_documents")
        task_desc = state.get("active_task_description", state.get("query", ""))
        result = retriever.retrieve(task_desc, verbose=verbose)
        return {
            "retrieved_context": result.merged,
            "current_node": "retrieve_documents",
        }

    # ── 6. Distill context ───────────────────────────────────────────────
    def distill_context(state: AgentState) -> AgentState:
        if verbose:
            print("\n🧹 Node: distill_context")
        task_desc = state.get("active_task_description", state.get("query", ""))
        raw_ctx = state.get("retrieved_context", "")
        result = distill_chain.run(query=task_desc, documents=raw_ctx)
        if verbose:
            print(f"   Distilled {len(raw_ctx)} → {len(result.relevant_content)} chars")
        return {
            "distilled_context": result.relevant_content,
            "current_node": "distill_context",
        }

    # ── 7. Reason and answer ─────────────────────────────────────────────
    def reason_and_answer(state: AgentState) -> AgentState:
        if verbose:
            print("\n🧠 Node: reason_and_answer")
        context = state.get("accumulated_evidence", "") + "\n" + state.get("distilled_context", "")
        task_desc = state.get("active_task_description", state.get("query", ""))
        result = reason_chain.run(context=context.strip(), question=task_desc)

        trace = list(state.get("reasoning_trace", []))
        trace.append(f"[Step {state.get('current_task_idx', 0) + 1}] {result.reasoning_chain}")

        evidence = state.get("accumulated_evidence", "")
        evidence += f"\n{result.answer}"

        if verbose:
            print(f"   Answer fragment: {result.answer[:120]}…")
        return {
            "accumulated_evidence": evidence.strip(),
            "reasoning_trace": trace,
            "current_node": "reason_and_answer",
        }

    # ── 8. Verify grounding ──────────────────────────────────────────────
    def verify_grounding(state: AgentState) -> AgentState:
        if verbose:
            print("\n🔍 Node: verify_grounding")
        context = state.get("distilled_context", state.get("retrieved_context", ""))
        answer = state.get("accumulated_evidence", "")
        result = verify_chain.run(context=context, answer=answer)
        if verbose:
            status = "✅ Grounded" if result.is_grounded else "⚠️  Unsupported claims found"
            print(f"   {status}")
        return {
            "is_grounded": result.is_grounded,
            "unsupported_claims": result.unsupported_claims,
            "current_node": "verify_grounding",
        }

    # ── 9. Advance to next task / replan ─────────────────────────────────
    def advance_or_replan(state: AgentState) -> AgentState:
        if verbose:
            print("\n🔄 Node: advance_or_replan")
        idx = state.get("current_task_idx", 0) + 1
        count = state.get("iteration_count", 0) + 1
        if verbose:
            print(f"   Moving to task index {idx}, iteration {count}")
        return {
            "current_task_idx": idx,
            "iteration_count": count,
            "current_node": "advance_or_replan",
        }

    # ── 10. Synthesize final response ────────────────────────────────────
    def synthesize_response(state: AgentState) -> AgentState:
        if verbose:
            print("\n✨ Node: synthesize_response")
        context = state.get("accumulated_evidence", "")
        question = state["query"]
        result = reason_chain.run(context=context, question=question)
        if verbose:
            print(f"   Final answer: {result.answer[:200]}…")
        return {
            "final_response": result.answer,
            "reasoning_trace": list(state.get("reasoning_trace", []))
            + [f"[Final] {result.reasoning_chain}"],
            "current_node": "synthesize_response",
        }

    return {
        "anonymize_query": anonymize_query,
        "generate_plan": generate_plan,
        "resolve_entities": resolve_entities,
        "route_task": route_task,
        "retrieve_documents": retrieve_documents,
        "distill_context": distill_context,
        "reason_and_answer": reason_and_answer,
        "verify_grounding": verify_grounding,
        "advance_or_replan": advance_or_replan,
        "synthesize_response": synthesize_response,
    }
