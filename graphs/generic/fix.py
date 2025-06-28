from langchain_core.messages import HumanMessage
from langchain_ollama.llms import OllamaLLM
import json
import yaml
import logging
import mlflow
import re
from typing import TypedDict

logger = logging.getLogger(__name__)

with open("config.yaml", "r") as file:
    MODEL = yaml.safe_load(file)["model"]
    llm = OllamaLLM(model=MODEL)
    
    
class FixCodeState(TypedDict):
    code: str
    errors: list[str]
    has_more: bool

def extract_response(response: str) -> FixCodeState:
    # logger.info(f"Extracting JSON from response: {response}")

    response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL) # Remove <think> tags if present

    metadata_match = re.search(r"<\s*METADATA\s*>\s*(\{.*?\})\s*<\s*/\s*METADATA\s*>", response, flags=re.DOTALL | re.IGNORECASE)
    code_match = re.search(r"<\s*CODE\s*>\s*(.*?)\s*<\s*/\s*CODE\s*>", response, flags=re.DOTALL | re.IGNORECASE)

    if not metadata_match:
        logger.warning("No metadata block found")
        mlflow.log_text(response, "outputs/response_without_metadata.txt")
        raise ValueError("No metadata block found in response")
    
    metadata_str = metadata_match.group(1)

    try:
        metadata = json.loads(metadata_str)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in METADATA: {e}")
        mlflow.log_text(metadata_str, "outputs/invalid_metadata.txt")
        raise ValueError(f"Invalid JSON in METADATA: {e}")
    
    code = code_match.group(1).strip() if code_match else ""
    if not code:
        logger.warning("No code block found")
        mlflow.log_text(response, "outputs/response_without_code.txt")

    return {
        "code": code,
        "error": metadata.get("error", "Unknown error"),
        "has_more": metadata.get("has_more", False)
    }

def ask(prompt: str) -> FixCodeState:
    response = llm.invoke([HumanMessage(content=prompt)])

    logger.debug(f"LLM response: {response}")
    return extract_response(response)