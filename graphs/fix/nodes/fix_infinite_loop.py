from graphs.fix.nodes.llm_utils import ask

def fix(code: str) -> dict:
    prompt = f"""
    # Instructions
    You are an autonomous agent responsible for finding and fixing infinite loops in Python code.
    You MUST carefully analyze the logic of the code and correct any loops that never terminate (e.g., `while True:` with no exit condition), **without altering the program’s intended behavior**.
    You MUST return the fixed code, ensuring that it is syntactically correct and logically sound.
    You MUST not make any comments or explanations, just return the fixed code.

    Return a <METADATA> tag with the following json:
    The "error" field should be an empty string if there are no errors, or the string "Infinite loop" if an infinite loop was found and fixed.
    The "has_more" field should be a boolean indicating whether there are more infinite loops in the code that were not fixed.
    After the <METADATA> tag, return a <CODE> tag containing the fixed code.

    You are allowed to:
    - Modify loop conditions.
    - Modify variables in the loop to ensure termination (in accordance with the program's logic).
    - Fix ONLY one infinite loop 

    You are NOT allowed to:
    - Remove loops that serve a functional purpose.
    - Change unrelated parts of the code.
    - Use breaks or returns to exit the loop.

    # Reasoning Strategy
    1. Analyze the control flow of the program.
    2. Identify any loop that lacks a termination condition or break path.
    3. Verify whether the loop has any possible exit in any execution path.
    4. If the loop is infinite and unintentional, fix it by adding a termination condition or modifying the loop variables.
    5. Preserve the overall logic and intent of the program.

    # Example Fix
    ## Input 1
    i = 0
    while i < 100:
        print("Still running")

    ## Output 1
    <METADATA>
    {{
        "error": "Infinite loop",
        "has_more": false
    }}
    </METADATA>
    <CODE>
    i = 0
    while i < 100:
        print("Still running")
        i += 1
    </CODE>

    ## Input 2
    i = 10
    while i > 0:
        print("Still running")
        j = 0
        while j < 4:
            print("Inner loop")

    ## Output 2
    <METADATA>
    {{
        "error": "Infinite loop",
        "has_more": true
    }}
    </METADATA>
    <CODE>
    i = 10
    while i > 0:
        print("Still running")
        j = 0
        while j < 4:
            print("Inner loop")
            j += 1
    </CODE>

    # Code to fix
    {code}
    """
    return ask(prompt)