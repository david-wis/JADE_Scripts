from fixers.llm_utils import ask

def fix(code: str) -> dict:
    prompt = f"""
    # Instructions
    You are an autonomous agent responsible for finding and fixing tautological or logically redundant `if` conditions in Python code.
    You MUST carefully analyze each conditional statement and correct any expression that is always true or always false (e.g., `if True:`, `if x == x:`), **without altering the program’s intended behavior**.
    You MUST return the fixed code, ensuring that it is syntactically correct and logically sound.
    You MUST not make any comments or explanations, just return the fixed code.

    You MUST return the code in a json format with three fields: "code", "error", and "has_more".
    Return a pure json object with no additional text or formatting.
    The "code" field should contain the fixed code.
    The "error" field should be an empty string if there are no errors, or the string "Tautology" if a tautology was found and fixed.
    The "has_more" field should be a boolean indicating whether there are more tautologies in the code that were not fixed.

    You are allowed to:
    - Remove or simplify tautological conditions.
    - Fix ONLY one tautology or contradiction

    You are NOT allowed to:
    - Remove conditionals that serve a functional purpose.
    - Change unrelated parts of the code.
    - Invent logic or behavior not present in the original code.
    - Change a tautology to an `if True:` or a contradiction to `if False:`.

    # Reasoning Strategy
    1. Analyze each `if`, `elif`, `else` condition.
    2. Identify expressions that are tautologies (always true or always false).
    3. Only fix one tautology or contradiction. Ignore the rest.

    # Example Fix
    Input:
    x = 5
    if x == x:
        print("This always runs")

    Fix:
    x = 5
    print("This always runs")

    # Code to fix
    {code}
    """
    return ask(prompt)
