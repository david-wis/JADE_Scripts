from langchain_core.messages import HumanMessage
from langchain_ollama.llms import OllamaLLM
import json
import yaml

with open("config.yaml", "r") as file:
    MODEL = yaml.safe_load(file)["model"]
    llm = OllamaLLM(model=MODEL)

def ask(prompt: str) -> dict:
    response = llm.invoke([HumanMessage(content=prompt)])
    try:
        if response.startswith("```json") and response.endswith("```"):
            response = response[7:-3]
        return json.loads(response)
    except json.JSONDecodeError:
        return {"code": response, "error": "???"}