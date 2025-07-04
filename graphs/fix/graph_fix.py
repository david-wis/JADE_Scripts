import yaml
from langgraph.graph import StateGraph
from typing import TypedDict
import logging
from graphs.fix.nodes import fix_tautologies
from graphs.fix.nodes import fix_syntax
from graphs.fix.nodes import fix_infinite_loop
from graphs.generic.fix import FixCodeState


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

with open("config.yaml", "r") as file:
    CONFIG = yaml.safe_load(file)
    STEPS = CONFIG["steps"]
    MODEL = CONFIG["model"]


def get_initial_state(initial_code) -> FixCodeState:
    return {
        "code": initial_code,
        "errors": [],
        "has_more": False,
    }


### Nodes
def apply_syntax_fixer(state: FixCodeState) -> FixCodeState:
    response = fix_syntax.fix(state["code"])
    state["code"] = response["code"].strip()
    return state


def apply_infinite_loop_fixer(state: FixCodeState) -> FixCodeState:
    response = fix_infinite_loop.fix(state["code"])
    logger.info(f"Response infinite loop: {response}")
    state["code"] = response["code"].strip()
    state["errors"].append(response["error"])
    state["has_more"] = response.get("has_more", False)

    return state


def apply_tautology_fixer(state: FixCodeState) -> FixCodeState:
    response = fix_tautologies.fix(state["code"])
    logger.info(f"Response tautology: {response}")
    state["code"] = response["code"].strip()
    state["errors"].append(response["error"])
    state["has_more"] = response.get("has_more", False)

    return state


logger.info(f"Starting the code fixing process with model: {MODEL}")

graph = StateGraph(FixCodeState)

graph_name = "CodeFix"

graph.add_node("FixSyntax", apply_syntax_fixer)

if STEPS["fix_infinite_loop"]:
    graph.add_node("FixLoop", apply_infinite_loop_fixer)

if STEPS["fix_tautologies"]:
    graph.add_node("FixTautologies", apply_tautology_fixer)

graph.set_entry_point("FixSyntax")
graph.add_edge(
    "FixSyntax", "FixLoop" if STEPS["fix_infinite_loop"] else "FixTautologies"
)

if STEPS["fix_infinite_loop"]:
    graph.add_conditional_edges(
        "FixLoop",
        lambda state: "FixTautologies" if not state["has_more"] else "FixLoop",
        ["FixTautologies", "FixLoop"],
    )

if STEPS["fix_tautologies"]:
    graph.add_conditional_edges(
        "FixTautologies",
        lambda state: "__end__" if not state["has_more"] else "FixTautologies",
        ["FixTautologies", "__end__"],
    )
