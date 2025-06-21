from identifiers.llm_utils import ask_detection


def detect_tautologies(code: str) -> list[str]:
    prompt = f"""
# Instructions
You are a static code analyzer responsible for identifying tautological or logically redundant `if` or `elif` conditions in Python code.

You MUST carefully analyze each conditional statement and report any expression that is always true or always false (e.g., `if True:`, `if x == x:`).

You MUST NOT modify the code or explain the reasoning.
You MUST only return the original lines that contain tautological `if` or `elif` conditions.

# Definition
A tautology is any conditional that always evaluates to `True` or `False`, regardless of input or context.
Examples include:
- `if True:`
- `if False:`
- `if 1 == 1:`
- `if x == x:` (when x is not changed)
- `if not False:`
- `if 0 > 1:`
- `if x != x:` (always false)

# Rules
- ONLY return lines that start with `if` or `elif` and are tautologies or contradictions.
- DO NOT include loops, print statements, or function definitions.
- DO NOT include conditionals that could evaluate differently based on program state (e.g., `if x > 0`)
- DO NOT include explanations, reasoning, or code not present in the input.
- Wrap the results in a <LINES>...</LINES> block.
- If no tautologies or contradictions are found, return an empty <LINES> block.

# Output format
<LINES>
Tautology: <line_number>: <code>
...
</LINES>

# Examples

## Input
1: x = 5
2: if x == x:
3:     print("This always runs")

## Output
<LINES>
Tautology: 2: if x == x:
</LINES>

## Input
1: if True:
2:     print("Hello")

## Output
<LINES>
Tautology: 1: if True:
</LINES>

## Input
1: if not False:
2:     print("Yep")

## Output
<LINES>
Tautology: 1: if not False:
</LINES>

## Input
1: if 1 == 1:
2:     print("Always equal")

## Output
<LINES>
Tautology: 1: if 1 == 1:
</LINES>

## Input
1: if 0 > 1:
2:     print("Never")

## Output
<LINES>
Tautology: 1: if 0 > 1:
</LINES>

## Input
1: if False:
2:     print("Never reached")

## Output
<LINES>
Tautology: 1: if False:
</LINES>

## Input
1: if x > 0:
2:     print("Positive")

## Output
<LINES>
</LINES>

## Input
1: x = True
2: if x:
3:     print("Maybe")

## Output
<LINES>
</LINES>

## Input
1: def test():
2:     if 2 == 2:
3:         return "OK"

## Output
<LINES>
Tautology: 2: if 2 == 2:
</LINES>

## Input
1: a = 10
2: b = 20
3: if a == b:
4:     print("Equal")

## Output
<LINES>
</LINES>

## Input
1: def redundant():
2:     x = 42
3:     if x == x:
4:         print("Trivial truth")

## Output
<LINES>
Tautology: 3: if x == x:
</LINES>

## Input
1: x = 0
2: while x < 5:
3:     if x == x:
4:         print(x)
5:     x += 1

## Output
<LINES>
Tautology: 3: if x == x:
</LINES>

## Input
1: if not (False or False):
2:     print("Always")

## Output
<LINES>
Tautology: 1: if not (False or False):
</LINES>

## Input
1: x = 10
2: if x != x:
3:     print("Impossible")

## Output
<LINES>
Tautology: 2: if x != x:
</LINES>

# Code to analyze
{code}
"""
    return ask_detection(prompt)
