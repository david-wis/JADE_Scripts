from langgraph.graph import StateGraph
from typing import TypedDict
import datetime

class CodeState(TypedDict):
    code: str
    errors: list[str]
    has_more: bool

### Nodes
def apply_syntax_fixer(state: CodeState) -> CodeState:
    from fixers import fix_syntax
    response = fix_syntax.fix(state["code"])
    state["code"] = response["code"].strip()
    return state

def apply_infinite_loop_fixer(state: CodeState) -> CodeState:
    from fixers import fix_infinite_loop
    response = fix_infinite_loop.fix(state["code"])
    print("Response infinite loop: ", response)
    state["code"] = response["code"].strip()
    state["errors"].append(response["error"])
    state["has_more"] = response.get("has_more", False)
    return state

def apply_tautology_fixer(state: CodeState) -> CodeState:
    from fixers import fix_tautologies
    response = fix_tautologies.fix(state["code"])
    print("Response tautology: ", response)
    state["code"] = response["code"].strip()
    state["errors"].append(response["error"])
    state["has_more"] = response.get("has_more", False)
    return state
###

graph = StateGraph(CodeState)

graph.add_node("FixSyntax", apply_syntax_fixer)
graph.add_node("FixLoop", apply_infinite_loop_fixer)
graph.add_node("FixTautologies", apply_tautology_fixer)

graph.set_entry_point("FixSyntax")

graph.add_edge("FixSyntax", "FixLoop")
graph.add_conditional_edges(
    "FixLoop",
    lambda state: "FixTautologies" if not state["has_more"] else "FixLoop",
    ["FixTautologies", "FixLoop"]
)
graph.add_conditional_edges(
    "FixTautologies",
    lambda state: "__end__" if not state["has_more"] else "FixTautologies",
    ["FixTautologies", "__end__"]
)

# graph.add_edge("FixLoop","FixTautologies")

app = graph.compile()

start = datetime.datetime.now()
result = app.invoke({
    "code": """
        def example():
            i = 0
            if i == 0:
                print("i is zero")
            while i < 10:
                print("This is an infinite loop")
                if i > -1:
                    print("Hello")
    """,
    "errors": [],
    "has_more": False
})

print("Code", result['code'])
print("Errors", result['errors'])
end = datetime.datetime.now()
elapsed_time = (end - start).total_seconds()
print(f"Elapsed time: {elapsed_time} seconds")

timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_file = f"./outputs/graph/{timestamp}_result.txt"

with open(output_file, "w") as f:
    f.write(result['code'])