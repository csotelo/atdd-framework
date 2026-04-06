"""
Grafo LangGraph del pipeline ATDD.

Flujo nominal:
    test_engineer → developer → tester → atf → END

Flujo de retry (tester o atf fallan):
    tester → developer → tester → ...   (hasta MAX_DEV_RETRIES)
    atf    → developer → tester → atf → ...

Flujo de bloqueo:
    cualquier nodo → BLOCKED → END
"""
from langgraph.graph import StateGraph, END

from atdd_orchestrator.domain.story import Status
from .state import PipelineState
from .nodes import test_engineer_node, developer_node, tester_node, atf_node

MAX_DEV_RETRIES = 3


def _route_after_test_engineer(state: PipelineState) -> str:
    if state["status"] == Status.READY_TO_DEV:
        return "developer"
    return END  # BLOCKED u otro estado inesperado


def _route_after_developer(state: PipelineState) -> str:
    if state["status"] == Status.READY_TO_TEST:
        return "tester"
    return END  # BLOCKED


def _route_after_tester(state: PipelineState) -> str:
    if state["status"] == Status.READY_TO_ATF:
        return "atf"
    if state["status"] == Status.READY_TO_DEV:
        if state["dev_retries"] < MAX_DEV_RETRIES:
            return "developer"
    return END  # BLOCKED o retries agotados


def _route_after_atf(state: PipelineState) -> str:
    if state["status"] == Status.DONE:
        return END
    if state["status"] == Status.READY_TO_DEV:
        if state["dev_retries"] < MAX_DEV_RETRIES:
            return "developer"
    return END  # BLOCKED o retries agotados


def build_pipeline() -> "CompiledGraph":
    g = StateGraph(PipelineState)

    g.add_node("test_engineer", test_engineer_node)
    g.add_node("developer", developer_node)
    g.add_node("tester", tester_node)
    g.add_node("atf", atf_node)

    g.set_entry_point("test_engineer")

    g.add_conditional_edges("test_engineer", _route_after_test_engineer, {
        "developer": "developer",
        END: END,
    })
    g.add_conditional_edges("developer", _route_after_developer, {
        "tester": "tester",
        END: END,
    })
    g.add_conditional_edges("tester", _route_after_tester, {
        "atf": "atf",
        "developer": "developer",
        END: END,
    })
    g.add_conditional_edges("atf", _route_after_atf, {
        "developer": "developer",
        END: END,
    })

    return g.compile()
