import os
import mlflow.langchain
import yaml


def load_langsmith_config():
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)
        if not config["langsmith"]["enable"]:
            return

        os.environ["LANGSMITH_TRACING"] = config["langsmith"]["tracing"]
        if config["langsmith"]["endpoint"]:
            os.environ["LANGSMITH_ENDPOINT"] = config["langsmith"]["endpoint"]
        if config["langsmith"]["apikey"]:
            os.environ["LANGSMITH_API_KEY"] = config["langsmith"]["apikey"]
        if config["langsmith"]["project"]:
            os.environ["LANGSMITH_PROJECT"] = config["langsmith"]["project"]

load_langsmith_config()

import mlflow
from langgraph.graph import StateGraph
from typing import TypedDict
import datetime
import os
import logging
import yaml

mlflow.set_tracking_uri("http://localhost:8080")
mlflow.langchain.autolog()

logger  = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class CodeState(TypedDict):
    code: str
    errors: list[str]
    has_more: bool

### Nodes
def apply_syntax_fixer(state: CodeState) -> CodeState:
    from fixers import fix_syntax
    response = fix_syntax.fix(state["code"])
    state["code"] = response["code"].strip()
    return state

def apply_infinite_loop_fixer(state: CodeState) -> CodeState:
    from fixers import fix_infinite_loop
    response = fix_infinite_loop.fix(state["code"])
    logger.info(f"Response infinite loop: {response}")
    state["code"] = response["code"].strip()
    state["errors"].append(response["error"])
    state["has_more"] = response.get("has_more", False)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    mlflow.log_text(str(response), f"./outputs/graph/{timestamp}_infinite_loop_fixed.txt")

    return state

def apply_tautology_fixer(state: CodeState) -> CodeState:
    from fixers import fix_tautologies
    response = fix_tautologies.fix(state["code"])
    logger.info(f"Response tautology: {response}")
    state["code"] = response["code"].strip()
    state["errors"].append(response["error"])
    state["has_more"] = response.get("has_more", False)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    mlflow.log_text(str(response), f"./outputs/graph/{timestamp}_tautology_fixed.txt")

    return state
###


with open("config.yaml", "r") as file:
    CONFIG = yaml.safe_load(file)
    STEPS = CONFIG["steps"]
    MODEL = CONFIG["model"]

logger.info(f"Starting the code fixing process with model: {MODEL}")

graph = StateGraph(CodeState)

graph.add_node("FixSyntax", apply_syntax_fixer)

if STEPS["fix_infinite_loop"]:
    graph.add_node("FixLoop", apply_infinite_loop_fixer)

if STEPS["fix_tautologies"]:
    graph.add_node("FixTautologies", apply_tautology_fixer)

graph.set_entry_point("FixSyntax")
graph.add_edge("FixSyntax", "FixLoop" if STEPS["fix_infinite_loop"] else "FixTautologies")

if STEPS["fix_infinite_loop"]:
    graph.add_conditional_edges(
        "FixLoop",
        lambda state: "FixTautologies" if not state["has_more"] else "FixLoop",
        ["FixTautologies", "FixLoop"]
    )

if STEPS["fix_tautologies"]:
    graph.add_conditional_edges(
        "FixTautologies",
        lambda state: "__end__" if not state["has_more"] else "FixTautologies",
        ["FixTautologies", "__end__"]
    )

app = graph.compile()

initial_code = """
    def example():
        i = 0
        if i == 0:
            print("i is zero")
        while i < 10:
            print("This is an infinite loop")
            if i > -1:
                print("Hello")
"""

with mlflow.start_run(run_name="LangGraph_CodeFix"):
    start = datetime.datetime.now()
    
    result = app.invoke({
        "code": initial_code,
        "errors": [],
        "has_more": False
    })

    end = datetime.datetime.now()
    elapsed_time = (end - start).total_seconds()

    # Parameters
    mlflow.log_param("model", MODEL)
    mlflow.log_param("nodes", list(graph.nodes.keys()))
    
    # Metrics
    mlflow.log_metric("execution_time", elapsed_time)
    mlflow.log_metric("num_errors", len(result["errors"]))

    # Artifacts
    os.makedirs("./outputs/graph", exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = f"./outputs/graph/{timestamp}_result.txt"
    with open(output_file, "w") as f:
        f.write(result["code"])
    
    mlflow.log_artifact(output_file)

    # Original code
    with open("./outputs/graph/original_code.txt", "w") as f:
        f.write(initial_code)
    mlflow.log_artifact("./outputs/graph/original_code.txt")

logger.info("Code fixing process completed.")