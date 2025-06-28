from graphs.generic.locate import ask_presence


def includes_numeric_words(code: str) -> dict:
    prompt = f"""
You are a static code analyzer.

Task:
- Determine if the code includes logic to detect **numeric words**.

Definition:
- A **numeric word** is any word or token composed **only of digits** (0–9).
- The code may check this using any method, such as:
    - character-by-character comparisons (e.g., '0' <= c AND c <= '9')
    - string methods like `.isdigit()`
    - logic that filters or flags words composed entirely of digits

Examples that should return <PRESENCE>YES</PRESENCE>:

1.
for char in palabra:
    if char < "0" or char > "9":
        es_numero = False

2.
if palabra.isdigit():
    return True

3.
for c in palabra:
    if not ("0" <= c <= "9"):
        return False

4.
if all(caracter.isdigit() for caracter in palabra):
    return True

Examples that should return <PRESENCE>NO</PRESENCE>:

1.
for palabra in lista:
    if palabra not in resultado:
        resultado.append(palabra)

2.
if len(palabra) > 3:
    return True

3.
def is_alpha(palabra):
    return palabra.isalpha()

4.
def filter_letters(lista):
    return [p for p in lista if p.isalpha()]

5.
import re
def filter_letters(palabra):
    return re.fullmatch(r"[a-zA-Z]+", palabra) is not None

6.
def filter_letters(word):
    for c in word:
        if not ("a" <= c <= "z" or "A" <= c <= "Z"):
            return False
    return True

Instructions:
- Return YES if the code includes logic to detect digit-only words.
- Return NO otherwise.

Output format (strict and exact):
<PRESENCE>YES</PRESENCE>
or
<PRESENCE>NO</PRESENCE>

Code to analyze:
{code}
"""
    return ask_presence(prompt)
