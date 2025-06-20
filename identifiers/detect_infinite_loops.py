from identifiers.llm_utils import ask


def detect_infinite_loops(code: str) -> list[str]:
    prompt = f"""
You are a static code analyzer.

Your task:
- Identify ONLY true infinite loops in the code.

Definition:
- A true infinite loop is a line of code that starts a loop and never ends. Valid cases:
  - `while True:` without a break
  - `while x == x:` when `x` is never modified

Strict rules:
- DO NOT INCLUDE:
  - Any line that starts with `if`, even if it looks like a tautology.
  - Any line that starts with `print`, `def`, `return`, etc.
  - Any loop that contains `break` or where the condition changes
- IGNORE any line that is not a `while` or `for` loop.
- Do NOT guess or infer.
- Do NOT include any explanation.
- Do NOT return a list or markdown.
- ONLY return actual code lines from the input that are clearly infinite loops.

Sample input and expected output:

# Input 1
1: i = 0
2: while i < 100:
3:     print("Still running")

# Expected Output 1
Infinite loop: 2: while i < 100:

# Input 2
1: i = 10
2: while i > 0:
3:     print("Still running")
4:     j = 0
5:     while j < 4:
6:         print("Inner loop")

# Expected Output 2
Infinite loop: 2: while i > 0:
Infinite loop: 5: while j < 4:

# Input 3
1: while True:
2:     print("Looping")

# Expected Output 3
Infinite loop: 1: while True:

# Input 4
1: x = 5
2: while x == x:
3:     print("No exit")

# Expected Output 4
Infinite loop: 2: while x == x:

Output format:
Infinite loop: <line_number>: <code>

Code:
{code}
"""
    return ask(prompt)
