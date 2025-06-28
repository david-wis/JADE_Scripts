
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

def group_by_function(function_names: list[str], code: str) -> dict[str, str]:
    """
    Group functions and their dependencies into a dictionary.
    """
    prompt = f"""
    # Instructions
    You are an autonomous agent responsible for grouping functions and their dependencies.
    You MUST carefully analyze the provided function names and their dependencies.
    You MUST NOT make any comments or explanations.
    You MUST return the result inside a single <FUNCTION name="f">...</FUNCTION> tag for each function, where "f" is the function name.
    You MUST return the code exactly as it is, without any modifications.

    If a function is called by another function, you MUST include it in the output.

    The functions names are provided in a list format (FUNCTION_NAMES).
    You MUST NOT include any function that is not in the FUNCTION_NAMES list and is not called by any function in the list.

    # Input 1
    FUNCTION_NAMES = ['f1', 'f2']
    def f1():
        pass
    def f2():
        pass

    # Output 1
    <FUNCTION name="f1">
    def f1():
        pass
    </FUNCTION>
    <FUNCTION name="f2">
    def f2():
        pass
    </FUNCTION>

    # Input 2
    FUNCTION_NAMES = ['a', 'b']
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
    <FUNCTION name="b">
    def b():
        pass
    </FUNCTION>

    # Code to analyze
    FUNCTION_NAMES = {function_names}
    {code}
    """
    response = llm.invoke(
        [HumanMessage(content=prompt)]
    )
    logger.debug(f"LLM response:\n{response}")
    return extract_functions_from_response(response)


    
if __name__ == "__main__":
    function_names = ["validar", "mostrar_lineas", "promedio_numeros", "sin_repetir"]
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

    grouped_functions = group_by_function(function_names, code2)
    print(grouped_functions)