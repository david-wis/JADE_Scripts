from langchain_core.messages import HumanMessage
from langchain_ollama.llms import OllamaLLM
import yaml
import logging
import mlflow
import re

logger = logging.getLogger(__name__)

# Load model config
with open("config.yaml", "r") as file:
    MODEL = yaml.safe_load(file)["model"]
    llm = OllamaLLM(model=MODEL, temperature=0.0, top_p=1.0, repeat_penalty=1.0)


def extract_lines_from_response(response: str) -> list[str]:
    """Extract <LINES>...</LINES> content as list of lines."""
    response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL)

    match = re.search(
        r"<\s*LINES\s*>(.*?)<\s*/\s*LINES\s*>",
        response,
        flags=re.DOTALL | re.IGNORECASE,
    )

    if not match:
        logger.warning("No <LINES> block found in response")
        mlflow.log_text(response, "outputs/response_without_lines.txt")
        return []

    lines_block = match.group(1)
    lines = [line.strip() for line in lines_block.strip().splitlines() if line.strip()]
    return lines


def extract_presence_from_response(response: str) -> str:
    """Extract <PRESENCE>YES|NO</PRESENCE> result."""
    response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL)

    match = re.search(
        r"<\s*PRESENCE\s*>(YES|NO)<\s*/\s*PRESENCE\s*>", response, flags=re.IGNORECASE
    )

    if not match:
        logger.warning("No <PRESENCE> block found in response")
        mlflow.log_text(response, "outputs/response_without_presence.txt")
        return "UNKNOWN"

    return match.group(1).upper()


def ask_location(prompt: str) -> list[str]:
    """Run LLM with prompt and extract lines."""
    response = llm.invoke([HumanMessage(content=prompt)])
    logger.debug(f"LLM response:\n{response}")
    return extract_lines_from_response(response)


def ask_presence(prompt: str) -> str:
    """Run LLM with prompt and extract presence (YES/NO)."""
    response = llm.invoke([HumanMessage(content=prompt)])
    logger.debug(f"LLM response:\n{response}")
    return extract_presence_from_response(response)
