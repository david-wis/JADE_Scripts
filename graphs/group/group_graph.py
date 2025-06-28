from typing import Callable, TypedDict
from langgraph.graph import StateGraph

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    level="INFO", format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

class CodeState(TypedDict):
    function_names: list[str]
    groups: dict[str, str]
    repeat: bool

def get_initial_state(initial_code: str, function_names: list[str]) -> dict:
    return {
        "function_names": function_names,
        "groups": {
            "default": initial_code
        },
        "repeat": False
    }

def apply_group_function(state: CodeState) -> CodeState:
    from graphs.group.nodes.group_functions import group_by_function

    code = state["groups"]["default"]
    function_names = state["function_names"]
    function_name = function_names.pop(0)
    repeat = len(function_names) > 0

    response = group_by_function(function_name, code)
    state = {
        "function_names": state["function_names"],
        "groups": {
            **state["groups"],
            **response
        },
        "repeat": repeat
    }
    return state


graph_builder = StateGraph(CodeState)

graph_name = "GroupGraph"

graph_builder.add_node("ApplyGroupFunction", apply_group_function)

graph_builder.add_conditional_edges(
    "ApplyGroupFunction",
    lambda state: "ApplyGroupFunction" if state["repeat"] else "__end__",
    ["ApplyGroupFunction", "__end__"]
)

graph_builder.set_entry_point("ApplyGroupFunction")

subgraph = graph_builder.compile()

def separate_in_groups(full_code: str, function_names: list[str]) -> dict[str, str]:
    groups_response = subgraph.invoke(get_initial_state(full_code, function_names))
    return groups_response["groups"]


