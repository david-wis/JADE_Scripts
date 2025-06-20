from langchain_core.messages import HumanMessage
from langchain_ollama.llms import OllamaLLM
import yaml
import json
import re

with open("config.yaml", "r") as file:
    MODEL = yaml.safe_load(file)["model"]
    llm = OllamaLLM(model=MODEL, temperature=0.0, top_p=1.0, repeat_penalty=1.0)


def ask(prompt: str) -> list[str]:
    response = llm.invoke([HumanMessage(content=prompt)])

    cleaned_response = re.sub(
        r"<think>.*?</think>", "", response, flags=re.DOTALL
    ).strip()

    return [line for line in cleaned_response.splitlines() if line.strip()]
