from langchain_core.messages import HumanMessage
from langchain_ollama.llms import OllamaLLM

MODEL = "codellama:13b"
# MODEL = "llama3.2:latest"
llm = OllamaLLM(model=MODEL)

def ask(prompt: str) -> str:
    response = llm.invoke([HumanMessage(content=prompt)])
    return response