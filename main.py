from langgraph.graph import StateGraph
from typing import TypedDict
import datetime

class CodeState(TypedDict):
    code: str
    has_errors: bool

### Nodes
def apply_syntax_fixer(state: CodeState) -> CodeState:
    from fixers import fix_syntax
    state["code"] = fix_syntax.fix(state["code"])
    return state

def apply_infinite_loop_fixer(state: CodeState) -> CodeState:
    from fixers import fix_infinite_loop
    state["code"] = fix_infinite_loop.fix(state["code"])
    return state

def apply_tautology_fixer(state: CodeState) -> CodeState:
    from fixers import fix_tautologies
    state["code"] = fix_tautologies.fix(state["code"])
    return state
###

graph = StateGraph(CodeState)

graph.add_node("FixSyntax", apply_syntax_fixer)
graph.add_node("FixLoop", apply_infinite_loop_fixer)
graph.add_node("FixTautologies", apply_tautology_fixer)

graph.set_entry_point("FixSyntax")

graph.add_edge("FixSyntax", "FixLoop")
graph.add_edge("FixLoop","FixTautologies")

app = graph.compile()

start = datetime.datetime.now()
result = app.invoke({
    "code": """
        def example():
            i = 0
            while i < 10:
                print("This is an infinite loop")
                if i > -1:
                    print("This is a tautology")
    """
})

print(result['code'])
end = datetime.datetime.now()
elapsed_time = (end - start).total_seconds()
print(f"Elapsed time: {elapsed_time} seconds")

timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_file = f"./outputs/graph/{timestamp}_result.txt"

with open(output_file, "w") as f:
    f.write(result['code'])