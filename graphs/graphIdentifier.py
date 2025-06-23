from langgraph.graph import StateGraph
from typing import TypedDict
from collections.abc import Callable
from identifiers.llm_utils import extract_presence_from_response
from identifiers.has_infinite_loops import has_infinite_loops
from identifiers.has_tautologies import has_tautologies
from identifiers.locate_infinite_loops import locate_infinite_loops
from identifiers.locate_tautologies import locate_tautologies

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

def generate_node_check_presence(target_name: str, target_checker: Callable[[str], dict]) -> Callable[[CodeState],CodeState]:
    def node_check_presence(state: CodeState) -> CodeState:
        state["presence"][target_name] = target_checker(state["code"])
        return state
    return node_check_presence

def generate_node_find(target_name: str, target_finder: Callable[[str], dict]) -> Callable[[CodeState],CodeState]:
    def node_find(state: CodeState) -> CodeState:
        state["errors"] += target_finder(state["code"])
        return state
    return node_find

def generate_condition_presence(target_name: str) -> Callable[[CodeState],str]:
    def condition_presence(state: CodeState) -> str:
        result = state["presence"].get(target_name, "NO")
        return result if result in ("YES", "NO") else "NO"
    return condition_presence


graph = StateGraph(CodeState)
graph_name = "CodeIdentifier"

graph.add_node("CheckInfiniteLoopPresence", generate_node_check_presence("infinite_loops", has_infinite_loops))
graph.add_node("LocateInfiniteLoops", generate_node_find("infinite_loops", locate_infinite_loops))
graph.add_node("CheckTautologyPresence", generate_node_check_presence("tautologies", has_tautologies))
graph.add_node("LocateTautologies", generate_node_find("tautologies", locate_tautologies)) 

graph.add_conditional_edges(
    "CheckInfiniteLoopPresence",
    generate_condition_presence("infinite_loops"),
    {"YES": "LocateInfiniteLoops", "NO": "CheckTautologyPresence"},
)

graph.add_edge("LocateInfiniteLoops", "CheckTautologyPresence")

graph.add_conditional_edges(
    "CheckTautologyPresence",
    generate_condition_presence("tautologies"),
    {"YES": "LocateTautologies", "NO": "__end__"},
)

graph.add_edge("LocateTautologies", "__end__")

graph.set_entry_point("CheckInfiniteLoopPresence")
