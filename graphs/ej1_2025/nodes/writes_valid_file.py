from identifiers.llm_utils import ask_presence


def writes_valid_file(code: str) -> str:
    prompt = f"""
    You are a static code analyzer.

    # Task:
    - Determine if the code writes to a file only when the input is valid.

    # Definition:
    - Writing to a file means using functions like `open()` to create or modify a file, followed by writing data to it using methods like `.write()` or `.writelines()`.
    - The input is valid if the function `validar` returns true.
    - You should return a tag <PRESENCE>YES</PRESENCE> if the code writes to a file when the input is valid, and <PRESENCE>NO</PRESENCE> if it does not.

    # Rules:
    - DO NOT return any explanations or reasoning.
    - ONLY return the presence tag <PRESENCE>YES</PRESENCE> or <PRESENCE>NO</PRESENCE>.
    - Consider that if there is no writing to a file, it should return <PRESENCE>NO</PRESENCE>.
    - If the code writes to a file regardless of input validity, it should return <PRESENCE>NO</PRESENCE>.
    - If the code writes to a file only when the input is valid, it should return <PRESENCE>YES</PRESENCE>.

    # Examples:

    ## Input 1

    if not validar(texto):
        raise ValueError("Invalid input")
    with open("output.txt", "w") as f:
        f.write("...")
    
    ## Output 1
    <PRESENCE>YES</PRESENCE>

    ## Input 2
    if validar(texto):
        file = open("output.txt", "w")
        file.write("...")
        file.close()
    
    ## Output 2
    <PRESENCE>YES</PRESENCE>

    ## Input 3
    if validar(texto):
        print("Valid input")
    with open("output.txt", "w") as f:
        f.write("This should not be written if input is invalid")

    ## Output 3
    <PRESENCE>NO</PRESENCE>

    ## Input 4
    with open("output.txt", "w") as f:
        f.write("This is always written regardless of input validity")
    
    ## Output 4
    <PRESENCE>NO</PRESENCE>

    # Output format (strict and exact):
    <PRESENCE>YES</PRESENCE>
    or 
    <PRESENCE>NO</PRESENCE>

    # Code to analyze:
    {code}
    """
    return ask_presence(prompt)

