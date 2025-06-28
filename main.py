import os
import mlflow.langchain
import yaml
import graphs
import mlflow
import datetime
import logging
import uuid
import graphs
import graphs.sin_repetir_graph
import graphs.graph1
import graphs.graphIdentifier
from langgraph.graph import StateGraph


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
with open("config.yaml", "r") as file:
    CONFIG = yaml.safe_load(file)
    MODEL = CONFIG["model"]
    MODE = CONFIG["mode"]
    INPUTS = CONFIG["inputs"]
    INPUT_QUANTITY = CONFIG["input_quantity"]

files = []
if os.path.exists(INPUTS):
    if os.path.isdir(INPUTS):
        files = [
            str(p)
            for p in os.listdir(INPUTS)
            if os.path.isfile(f"{str(os.path.dirname(INPUTS))}/{p}")
        ][:INPUT_QUANTITY]
    elif os.path.isfile(INPUTS):
        files = [str(os.path.basename(INPUTS))]
    else:
        raise ValueError("INPUT NOT FOUND")
else:
    raise ValueError("INPUT NOT FOUND")

mlflow.set_tracking_uri("http://localhost:8080")
mlflow.langchain.autolog()

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

graph_dict = {
    "fix": graphs.graph1,
    "locate": graphs.graphIdentifier,
    "ej1_2025": graphs.sin_repetir_graph
}

# mlflow.set_experiment(MODE)
graph_strategy = graph_dict.get(MODE, graphs.graph1)
graph : StateGraph = graph_strategy.graph
graph_name = graph_strategy.graph_name

app = graph.compile()

execution_id = uuid.uuid4()

for file_name in files:
    print(file_name)
    if file_name.endswith(".txt") or file_name.endswith(".py"):
        with open(f"{os.path.dirname(INPUTS)}/{file_name}", "r") as f:
            initial_code = f.read()
    dataset_name = file_name.split(".")[0]
    output_folder = f"./outputs/{execution_id}-{dataset_name}"

    if MODE == "locate":
        initial_code = "\n".join(
            f"{i + 1}: {line}"
            for i, line in enumerate(initial_code.strip().splitlines())
        )

    with mlflow.start_run(run_name=f"{graph_name}-{execution_id}-{dataset_name}"):
        start = datetime.datetime.now()
        result = app.invoke(graph_strategy.get_initial_state(initial_code))

        end = datetime.datetime.now()
        elapsed_time = (end - start).total_seconds()

        # Parameters
        mlflow.log_param("nodes", list(graph.nodes.keys()))
        mlflow.log_param("execution_id", execution_id)
        mlflow.log_param("dataset_name", dataset_name)

        # Metrics
        mlflow.log_metric("execution_time", elapsed_time)
        mlflow.log_metric("num_errors", len(result["errors"]))

        # Artifacts
        os.makedirs(output_folder, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_file = f"{output_folder}/{timestamp}_result.txt"
        errors_file = f"{output_folder}/{timestamp}_errors.txt"

        with open(output_file, "w") as f:
            f.write(result["code"])

        with open(errors_file, "w") as f:
            f.write("\n".join(result["errors"]))

        mlflow.log_artifact(output_file)
        mlflow.log_artifact(errors_file)

        # Original code
        with open(f"{output_folder}/original_code.txt", "w") as f:
            f.write(initial_code)
        mlflow.log_artifact(f"{output_folder}/original_code.txt")


logger.info("Code fixing process completed.")
