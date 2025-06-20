import os
import mlflow.langchain
import yaml
import graphs
import mlflow
import datetime
import logging

import graphs.graph1

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
    

mlflow.set_tracking_uri("http://localhost:8080")
mlflow.langchain.autolog()

logger  = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

graph = graphs.graph1.graph 
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
    mlflow.set_active_model(name=MODEL.split(':')[0])
    mlflow.log_param("nodes", list(graph.nodes.keys()))
    
    mlflow.log_trace
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