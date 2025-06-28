
from graphs.locate.nodes.llm_utils import ask_presence
def has_sort(code: str) -> dict:
    prompt = f"""
# Instructions
You are a static code analyzer responsible for identifying whether the code is implementing the feature of **sorting words by their length**.

# Definition
Sorting by length means that a list of words is arranged in ascending or descending order based on the number of characters in each word.

Valid sorting implementations include:
- Using the `sorted()` function with `key=len`
- Using `.sort()` with `key=len`
- Custom sorting functions that use the `len()` of elements to determine order

Examples:
- sorted(words, key=len)
- words.sort(key=len)
- sorted(words, key=lambda w: len(w))
- words.sort(key=lambda x: len(x))

# Rules
- BE OPEN about what can be considered sorting
- ONLY return lines that are directly involved in sorting the list of words by their length.
- DO NOT return lines that sort by other criteria (e.g., alphabetically).
- DO NOT include lines that only define the list or iterate over it.
- DO NOT include any explanation or reasoning.
- Wrap the result in a <LINES>...</LINES> block.
- If no sorting by length is detected, return an empty <LINES> block.

# Output format
<PRESENCE>YES</PRESENCE>
or
<PRESENCE>NO</PRESENCE>

# Examples

## Input
1: words = ["pear", "banana", "kiwi"]
2: sorted_words = sorted(words, key=len)

## Output
<PRESENCE>YES</PRESENCE>

## Input
1: words = ["pear", "banana", "kiwi"]
2: words.sort(key=lambda w: len(w))

## Output
<PRESENCE>YES</PRESENCE>

## Input
1: words = ["pear", "banana", "kiwi"]
2: sorted_words = sorted(words)

## Output
<PRESENCE>NO</PRESENCE>

## Input
1: words = ["pear", "banana", "kiwi"]
2: def by_length(w): return len(w)
3: words.sort(key=by_length)

## Output
<PRESENCE>YES</PRESENCE>


## Input
1: words = ["pear", "banana", "kiwi"]
2: for i in range(len(words)):
3:     for j in range(len(words) - i - 1):
4:         if len(words[j]) > len(words[j + 1]):
5:             words[j], words[j + 1] = words[j + 1], words[j]

## Output
<PRESENCE>YES</PRESENCE>


# Code to analyze
{code}
"""
    return ask_presence(prompt)
