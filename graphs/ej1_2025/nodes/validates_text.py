from graphs.generic.locate import ask_presence


def validates_text(code: str) -> dict:
    prompt = f"""
You are a static code analyzer.

Task:
- Determine if the function `validar(texto)` is **explicitly called** inside a function named `sin_repetir`, and its result is used to control the flow **before any further processing**.

Strict requirements:
- The function `validar(texto)` must be **called inside `sin_repetir`**.
- The result of that call must be used to influence the flow (e.g., via `if`, `return`, etc.).
- It is NOT enough for `validar` to be defined or called in a different function.
- It is NOT enough if `validar(texto)` is defined but never called.

Accepted patterns:
- Direct check:
    - `if not validar(texto): return`
    - `if validar(texto): ...`
- Indirect check via variable:
    - `result = validar(texto)` followed by `if not result:` or `if result:`

Examples that should return <PRESENCE>YES</PRESENCE>:

1.
def sin_repetir(texto):
    if not validar(texto):
        return
    print("processing")

2.
def sin_repetir(texto):
    is_valid = validar(texto)
    if is_valid:
        print("ok")

3.
def sin_repetir(texto):
    result = validar(texto)
    if not result:
        print("Invalid")
        return
    words = texto.split()

Examples that should return <PRESENCE>NO</PRESENCE>:

1.
def sin_repetir(texto):
    print("Hello")

2.
def sin_repetir(texto):
    words = texto.split()

3.
def validar(texto):
    return True

def another_function(texto):
    if not validar(texto):
        return

def sin_repetir(texto):
    process(texto)

4.
def sin_repetir(texto):
    if texto != "":
        return

Instructions:
- Return YES only if:
    - The function `validar(texto)` is called **inside `sin_repetir`**
    - and its result is used to control the logic (e.g. using `if`, `return`, etc.)

Output format (strict and exact):
<PRESENCE>YES</PRESENCE>
or
<PRESENCE>NO</PRESENCE>

Code to analyze:
{code}
"""
    return ask_presence(prompt)
