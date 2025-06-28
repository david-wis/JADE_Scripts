from typing import Callable, TypedDict
from langgraph.graph import StateGraph

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    level="INFO", format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

class CodeState(TypedDict):
    code: str
    function_names: list[str]
    groups: dict[str, str]

def get_initial_state(initial_code: str, function_names: list[str]) -> dict:
    return {
        "function_names": function_names,
        "groups": {
            "default": initial_code
        }
    }

def apply_group_function(state: CodeState) -> CodeState:
    from graphs.group.nodes.group_functions import group_by_function

    code = state["groups"]["default"]
    response = group_by_function(state["function_names"], code)
    state = {
        "code": code,
        "function_names": state["function_names"],
        "groups": {
            **response # type: ignore
        }
    }
    return state


graph_builder = StateGraph(CodeState)

graph_name = "GroupGraph"

graph_builder.add_node("apply_group_function", apply_group_function)

graph_builder.set_entry_point("apply_group_function")

subgraph = graph_builder.compile()

def separate_in_groups(full_code: str, function_names: list[str]) -> dict[str, str]:
    groups_response = subgraph.invoke(get_initial_state(full_code, function_names))
    return groups_response["groups"]


