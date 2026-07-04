"""Unit tests for graph structure and routing logic."""

from intelliquery.agents.state import AgentState
from intelliquery.agents.graph import _route_after_task, _should_continue


class TestRouteAfterTask:
    def test_routes_retrieve(self):
        state: AgentState = {
            "execution_plan": [
                {"step": 1, "action": "RETRIEVE", "description": "Find X"}
            ],
            "current_task_idx": 0,
        }
        assert _route_after_task(state) == "retrieve_documents"

    def test_routes_reason(self):
        state: AgentState = {
            "execution_plan": [
                {"step": 1, "action": "REASON", "description": "Deduce Y"}
            ],
            "current_task_idx": 0,
        }
        assert _route_after_task(state) == "reason_and_answer"

    def test_routes_synthesize_when_done(self):
        state: AgentState = {
            "execution_plan": [
                {"step": 1, "action": "RETRIEVE", "description": "Find X"}
            ],
            "current_task_idx": 1,  # Past the end
        }
        assert _route_after_task(state) == "synthesize_response"


class TestShouldContinue:
    def test_continues_when_tasks_remain(self):
        state: AgentState = {
            "execution_plan": [
                {"step": 1, "action": "RETRIEVE", "description": "A"},
                {"step": 2, "action": "REASON", "description": "B"},
            ],
            "current_task_idx": 1,
            "iteration_count": 1,
        }
        assert _should_continue(state) == "route_task"

    def test_stops_when_all_done(self):
        state: AgentState = {
            "execution_plan": [
                {"step": 1, "action": "RETRIEVE", "description": "A"},
            ],
            "current_task_idx": 1,
            "iteration_count": 1,
        }
        assert _should_continue(state) == "synthesize_response"

    def test_stops_at_max_iterations(self):
        state: AgentState = {
            "execution_plan": [
                {"step": 1, "action": "RETRIEVE", "description": "A"},
                {"step": 2, "action": "RETRIEVE", "description": "B"},
            ],
            "current_task_idx": 0,
            "iteration_count": 10,  # At the cap
        }
        assert _should_continue(state) == "synthesize_response"
