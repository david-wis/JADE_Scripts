from langgraph.graph import StateGraph
from typing import TypedDict
from collections.abc import Callable
from graphs.ej1_2025.nodes.sorts import sorts
from graphs.ej1_2025.nodes.has_sort import has_sort
from graphs.ej1_2025.nodes.validates_text import validates_text
from graphs.ej1_2025.nodes.writes_valid_file import writes_valid_file
from graphs.ej1_2025.nodes.includes_numeric_words import includes_numeric_words

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


def generate_node_check_presence(
    target_name: str, target_checker: Callable[[str], dict]
) -> Callable[[CodeState], CodeState]:
    def node_check_presence(state: CodeState) -> CodeState:
        state["presence"][target_name] = target_checker(state["code"])
        return state

    return node_check_presence


def generate_node_find(
    target_name: str, target_finder: Callable[[str], dict]
) -> Callable[[CodeState], CodeState]:
    def node_find(state: CodeState) -> CodeState:
        state["errors"] += target_finder(state["code"])
        return state

    return node_find


def generate_condition_presence(target_name: str) -> Callable[[CodeState], str]:
    def condition_presence(state: CodeState) -> str:
        result = state["presence"].get(target_name, "NO")
        return result if result in ("YES", "NO") else "NO"

    return condition_presence


graph = StateGraph(CodeState)
graph_name = "SinRepetirIdentifier"

graph.add_node("ValidatesText", generate_node_check_presence("validates_text", validates_text))
graph.add_node("IncludesNumericWords", generate_node_check_presence("includes_numeric_words", includes_numeric_words))
graph.add_node("Sorts", generate_node_check_presence("sorts", has_sort))
graph.add_node("WritesValidFile",generate_node_check_presence("writes_valid_file", writes_valid_file))


graph.add_edge("ValidatesText","IncludesNumericWords")
graph.add_edge("IncludesNumericWords","Sorts")
graph.add_edge("Sorts","WritesValidFile")
graph.add_edge("WritesValidFile","__end__")

graph.set_entry_point("ValidatesText")

if __name__ == "__main__":
    with open("inputs/alum_36 copy.py", "r") as file:
        code2 = file.read()

    # result = has_sort(code2)
    result = writes_valid_file(code2)
    print(result)
