from identifiers.llm_utils import ask_presence


def presence(code: str) -> str:
    prompt = f"""
# Instructions
You are a static code analyzer responsible for identifying whether a piece of Python code contains ANY tautological or logically redundant condition.

You MUST carefully analyze the logic of the code and determine if there is at least one conditional statement that is always `True` or always `False`.

You MUST NOT explain your answer or include line numbers.
You MUST return your result inside a single <PRESENCE>...</PRESENCE> tag.

# Definition
A tautology is a conditional that always evaluates to `True` or `False`, regardless of context or input. Examples include:
- `if True:`
- `if False:`
- `if 1 == 1:`
- `if x == x:` (when `x` is not modified)
- `if not False:`
- `if 0 > 1:` (always false)
- `if x != x:` (always false)

# Rules
- ONLY analyze lines starting with `if` or `elif`.
- IGNORE all other lines like `while`, `print`, `return`, `def`, etc.
- DO NOT consider any condition that may vary with input or context, like `if x > 5`, `if x == y`, etc.
- DO NOT GUESS. Only return YES if at least one **clear tautology or contradiction** is present.

# Output format
Return exactly:
<PRESENCE>YES</PRESENCE>
or
<PRESENCE>NO</PRESENCE>

# Examples

## Input
1: x = 5
2: if x == x:
3:     print("Yes")

## Output
<PRESENCE>YES</PRESENCE>

## Input
1: if True:
2:     print("Always")

## Output
<PRESENCE>YES</PRESENCE>

## Input
1: if not False:
2:     print("Valid")

## Output
<PRESENCE>YES</PRESENCE>

## Input
1: if 1 == 1:
2:     print("Math")

## Output
<PRESENCE>YES</PRESENCE>

## Input
1: if False:
2:     print("Never")

## Output
<PRESENCE>YES</PRESENCE>

## Input
1: if 0 > 1:
2:     print("No")

## Output
<PRESENCE>YES</PRESENCE>

## Input
1: x = 10
2: if x != x:
3:     print("Nonsense")

## Output
<PRESENCE>YES</PRESENCE>

## Input
1: if x > 5:
2:     print("Maybe")

## Output
<PRESENCE>NO</PRESENCE>

## Input
1: x = True
2: if x:
3:     print("Conditional")

## Output
<PRESENCE>NO</PRESENCE>

## Input
1: a = 10
2: b = 10
3: if a == b:
4:     print("Equal")

## Output
<PRESENCE>NO</PRESENCE>

## Input
1: def test():
2:     if 2 == 2:
3:         return True

## Output
<PRESENCE>YES</PRESENCE>

## Input
1: def check():
2:     if x == x:
3:         return True

## Output
<PRESENCE>YES</PRESENCE>

Now analyze the following code:

{code}
"""
    return ask_presence(prompt)
