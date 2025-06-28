
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

def extract_functions_from_response(response: str) -> dict[str, str]:
    """
    Extract functions and their code from the LLM response.
    The response should be in the format:
    <FUNCTION name="function_name">
    def function_name():
        # function code
    </FUNCTION>
    """
    functions = {}
    lines = response.splitlines()
    current_function = None
    current_code = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("<FUNCTION name="):
            # Guardar función anterior si quedó sin cerrar
            if current_function is not None:
                functions[current_function] = "\n".join(current_code)
            match = re.search(r'name="([^"]+)"', stripped)
            if match:
                current_function = match.group(1)
                current_code = []
        elif stripped.startswith("</FUNCTION>"):
            if current_function is not None:
                functions[current_function] = "\n".join(current_code)
                current_function = None
                current_code = []
        elif current_function is not None:
            current_code.append(line)

    if current_function is not None and current_code:
        functions[current_function] = "\n".join(current_code)

    return functions

def group_by_function(function_name: str, code: str) -> dict[str, str]:
    """
    Group functions and their dependencies into a dictionary.
    """
    prompt = f"""
    # Instructions
    You are an autonomous agent responsible for finding functions and their dependencies.
    You MUST carefully analyze the provided function name and its dependencies.
    You MUST NOT make any comments or explanations.
    You MUST return the result inside a single <FUNCTION name="f">...</FUNCTION> tag, where "f" is the function name.
    You MUST return the code exactly as it is, without any modifications.

    If a function is called by the provided function or its dependencies, you MUST include it in the output.

    Only one function names is provided (FUNCTION_NAME).
    You MUST NOT include any function that is not called FUNCTION_NAME and is not called by FUNCTION_NAME.

    # Input 1
    FUNCTION_NAME = 'f1'
    def f1():
        pass
    def f2():
        pass

    # Output 1
    <FUNCTION name="f1">
    def f1():
        pass
    </FUNCTION>

    # Input 2
    FUNCTION_NAME = 'a'
    def d():
        pass

    def a():
        i = 0
        c(i)
        d()

    def b():
        pass

    def e():
        pass

    def c(i):
        print(i)

    # Output 2
    <FUNCTION name="a">
    def d():
        pass

    def a():
        i = 0
        c(i)
        d()

    def c(i):
        print(i)
    </FUNCTION>

    # Input 3
    FUNCTION_NAME = 'validate'
    def validar():
        return True
    
    def mostrar_lineas():
        return "Lineas"
    
    # Output 3

    # Code to analyze
    FUNCTION_NAME = {function_name}
    {code}
    """
    response = llm.invoke(
        [HumanMessage(content=prompt)]
    )
    logger.debug(f"LLM response:\n{response}")
    return extract_functions_from_response(response)


    
if __name__ == "__main__":
    function_name = "validar"
    code = """
    def sum(a, b):
        return a + b

    def validate_input(a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero")

    def divide():
        validate_input(a, b)
        return a / b
    
    def multiply(a, b):
        return a * b 
    """
    with open("inputs/alum_36.py", "r") as file:
        code2 = file.read()

    grouped_functions = group_by_function(function_name, code2)
    print(grouped_functions)