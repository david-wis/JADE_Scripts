from langgraph.graph import StateGraph
from typing import TypedDict
from identifiers.detect_infinite_loops import detect_infinite_loops
from identifiers.detect_tautologies import detect_tautologies


class CodeState(TypedDict):
    code: str
    errors: list[str]


def node_detect_loops(state: CodeState) -> CodeState:
    state["errors"] += detect_infinite_loops(state["code"])
    return state


def node_detect_tautologies(state: CodeState) -> CodeState:
    state["errors"] += detect_tautologies(state["code"])
    return state


graph = StateGraph(CodeState)
graph_name = "CodeIdentifier"

graph.add_node("DetectLoops", node_detect_loops)
graph.add_node("DetectTautologies", node_detect_tautologies)

graph.set_entry_point("DetectLoops")
graph.add_edge("DetectLoops", "DetectTautologies")
