from graphs.locate.nodes.llm_utils import ask_location


def locate_infinite_loops(code: str) -> list[str]:
    prompt = f"""
# Instructions
You are a static code analyzer responsible for identifying infinite loops in Python code.
You MUST carefully analyze the logic of the code and report any loops that never terminate.

You MUST NOT modify the code or explain the reasoning.
You MUST return the result inside a single <LINES>...</LINES> tag.

# Definition
A true infinite loop is a loop that never terminates under any execution path. Examples include:
- `while True:` with no `break`
- `while x == x:` where `x` is never changed inside the loop
- `for _ in itertools.cycle(...)` or any loop over an unbounded iterator

# Rules
- ONLY include lines that start a `while` or `for` loop.
- IGNORE lines that start with `if`, `print`, `return`, `def`, etc.
- DO NOT include any loop that:
  - contains a `break`
  - modifies its own condition inside the loop
  - is clearly bounded (e.g., `for i in range(10)` or `while x < 5` with `x += 1`)
- DO NOT GUESS. Be conservative and only mark clearly infinite loops.
- DO NOT include explanations, markdown, or commentary.
- Output must consist ONLY of actual code lines present in the input.

# Output format
Wrap the result in:
<LINES>
Infinite loop: <line_number>: <code>
...
</LINES>

If no infinite loops are found, return:
<LINES>
</LINES>

# Examples

## Input
1: i = 0
2: while i < 100:
3:     print("Still running")

## Output
<LINES>
Infinite loop: 2: while i < 100:
</LINES>

## Input
1: while True:
2:     print("Looping")

## Output
<LINES>
Infinite loop: 1: while True:
</LINES>

## Input
1: x = 5
2: while x == x:
3:     print("No exit")

## Output
<LINES>
Infinite loop: 2: while x == x:
</LINES>

## Input
1: for i in range(5):
2:     print(i)

## Output
<LINES>
</LINES>

## Input
1: while True:
2:     print("processing")
3:     break

## Output
<LINES>
</LINES>

## Input
1: x = 10
2: while x > 0:
3:     print(x)
4:     x -= 1

## Output
<LINES>
</LINES>

## Input
1: x = 10
2: while x > 0:
3:     print(x)

## Output
<LINES>
Infinite loop: 2: while x > 0:
</LINES>

## Input
1: for i in range(10):
2:     while True:
3:         print("inner")

## Output
<LINES>
Infinite loop: 2: while True:
</LINES>

## Input
1: for i in range(10):
2:     for j in range(5):
3:         print(i, j)

## Output
<LINES>
</LINES>

## Input
1: x = 0
2: while x < 5:
3:     if x % 2 == 0:
4:         print(x)
5:     x += 1

## Output
<LINES>
</LINES>

## Input
1: while False == False:
2:     print("never ends")

## Output
<LINES>
Infinite loop: 1: while False == False:
</LINES>

## Input
1: def loop():
2:     while True:
3:         return

## Output
<LINES>
</LINES>

## Input
1: import itertools
2: for _ in itertools.cycle([1, 2]):
3:     print("looping")

## Output
<LINES>
Infinite loop: 2: for _ in itertools.cycle([1, 2]):
</LINES>

## Input
1: i = 10
2: while i > 0:
3:     print("Counting")
4:     j = 0
5:     while j < 3:
6:         print("Inner")
7:         j += 1

## Output
<LINES>
Infinite loop: 2: while i > 0:
</LINES>

# Code to analyze
{code}
"""
    return ask_location(prompt)
