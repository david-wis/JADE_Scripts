from langgraph.graph import StateGraph
from typing import TypedDict

from identifiers.llm_utils import extract_presence_from_response
from identifiers.has_infinite_loops import has_infinite_loops
from identifiers.has_tautologies import has_tautologies
from identifiers.detect_infinite_loops import detect_infinite_loops
from identifiers.detect_tautologies import detect_tautologies


class CodeState(TypedDict):
    code: str
    errors: list[str]
    presence: dict[str, str]


def get_initial_state(initial_code) -> CodeState:
    return {
        "code": initial_code,
        "errors": [],
        "presence": {},
    }


def node_check_infinite_loop_presence(state: CodeState) -> CodeState:
    state["presence"]["infinite_loops"] = has_infinite_loops(state["code"])
    return state


def node_detect_infinite_loops(state: CodeState) -> CodeState:
    state["errors"] += detect_infinite_loops(state["code"])
    return state


def node_check_tautology_presence(state: CodeState) -> CodeState:
    state["presence"]["tautologies"] = has_tautologies(state["code"])
    return state


def node_detect_tautologies(state: CodeState) -> CodeState:
    state["errors"] += detect_tautologies(state["code"])
    return state


def condition_infinite_loop_presence(state: CodeState) -> str:
    result = state["presence"].get("infinite_loops", "NO")
    return result if result in ("YES", "NO") else "NO"


def condition_tautology_presence(state: CodeState) -> str:
    result = state["presence"].get("tautologies", "NO")
    return result if result in ("YES", "NO") else "NO"


graph = StateGraph(CodeState)
graph_name = "CodeIdentifier"

graph.add_node("CheckInfiniteLoopPresence", node_check_infinite_loop_presence)
graph.add_node("DetectInfiniteLoops", node_detect_infinite_loops)
graph.add_node("CheckTautologyPresence", node_check_tautology_presence)
graph.add_node("DetectTautologies", node_detect_tautologies)

graph.add_conditional_edges(
    "CheckInfiniteLoopPresence",
    condition_infinite_loop_presence,
    {"YES": "DetectInfiniteLoops", "NO": "CheckTautologyPresence"},
)

graph.add_edge("DetectInfiniteLoops", "CheckTautologyPresence")

graph.add_conditional_edges(
    "CheckTautologyPresence",
    condition_tautology_presence,
    {"YES": "DetectTautologies", "NO": "__end__"},
)

graph.add_edge("DetectTautologies", "__end__")

graph.set_entry_point("CheckInfiniteLoopPresence")
