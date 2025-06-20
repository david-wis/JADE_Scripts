from identifiers.llm_utils import ask


def detect_tautologies(code: str) -> list[str]:
    prompt = f"""
You are a static code analyzer.

Task:
- Detect tautologies in Python code.

Definition:
- A tautology is a conditional that always evaluates to True, such as:
  - `if x == x`
  - `if True`
  - `if i == 0` when `i` was just assigned `0` and not modified before

Rules:
- Code is line-numbered (e.g., "3: if x == x:")
- Output one real tautology per line
- Format exactly as:
  Tautology: <line_number>: <code>
- Do NOT include any non-tautological code
- Do NOT guess
- Do NOT include `while` statements
- Do NOT return explanations, markdown, or list brackets

Sample code inputs:

# Input 1
1: x = 1
2: if x == x:
3:     print("match")
4: y = False
5: if y:
6:     print("never")

# Expected Output 1
Tautology: 2: if x == x:

# Input 2
1: z = 10
2: if True:
3:     print(z)
4: if z == z:
5:     print("ok")

# Expected Output 2
Tautology: 2: if True:
Tautology: 4: if z == z:

# Input 3
1: i = 0
2: if i == 0:
3:     print("start")
4: i = 1
5: if i == 0:
6:     print("no")

# Expected Output 3
Tautology: 2: if i == 0:

1: i = 0
2: while i < 5:
3:     print(i)
4: if i > 5:
5:     print("done")

# Expected Output 4
(none)

# Input 5 
1: while True:
2:     print("looping")
3: x = 5
4: if x > 0:
5:     print("ok")

# Expected Output 5
(none)

Output format:
Tautology: <line_number>: <code>

Code:
{code}
"""
    return ask(prompt)
