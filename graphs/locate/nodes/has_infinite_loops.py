from graphs.locate.nodes.llm_utils import ask_presence


def has_infinite_loops(code: str) -> str:
    prompt = f"""
# Instructions
You are a static code analyzer responsible for identifying whether a piece of Python code contains ANY true infinite loop.

You MUST carefully analyze the control flow and determine if there is at least one loop that never terminates.

You MUST NOT explain your answer or include line numbers.
You MUST return your result inside a single <PRESENCE>...</PRESENCE> tag.

# Definition
A true infinite loop is a loop that never terminates under any execution path. Examples include:
- `while True:` with no `break`
- `while x == x:` where `x` is never modified inside the loop
- `for _ in itertools.cycle(...)` or any loop over an unbounded iterator

# Rules
- ONLY count loops that start with `while` or `for`.
- IGNORE all other lines such as `if`, `print`, `def`, `return`, etc.
- A loop is NOT infinite if:
  - It contains a `break` or `return`
  - Its condition changes inside the body (e.g., `x += 1`)
  - It’s bounded by an iterator like `range(...)`
- DO NOT GUESS. Be conservative. Only report YES if the infinite loop is certain.

# Output format
Return exactly:
<PRESENCE>YES</PRESENCE>
or
<PRESENCE>NO</PRESENCE>

# Examples

## Input
1: i = 0
2: while i < 100:
3:     print("Still running")

## Output
<PRESENCE>YES</PRESENCE>

## Input
1: while True:
2:     print("Looping")

## Output
<PRESENCE>YES</PRESENCE>

## Input
1: x = 5
2: while x == x:
3:     print("No exit")

## Output
<PRESENCE>YES</PRESENCE>

## Input
1: for i in range(5):
2:     print(i)

## Output
<PRESENCE>NO</PRESENCE>

## Input
1: while True:
2:     print("processing")
3:     break

## Output
<PRESENCE>NO</PRESENCE>

## Input
1: x = 10
2: while x > 0:
3:     print(x)
4:     x -= 1

## Output
<PRESENCE>NO</PRESENCE>

## Input
1: for i in range(10):
2:     while True:
3:         print("inner")

## Output
<PRESENCE>YES</PRESENCE>

## Input
1: while False == False:
2:     print("never ends")

## Output
<PRESENCE>YES</PRESENCE>

## Input
1: def loop():
2:     while True:
3:         return

## Output
<PRESENCE>NO</PRESENCE>

## Input
1: i = 10
2: while i > 0:
3:     print("Counting")
4:     j = 0
5:     while j < 3:
6:         print("Inner")
7:         j += 1

## Output
<PRESENCE>YES</PRESENCE>

# Code to analyze
{code}
"""
    return ask_presence(prompt)
