import os
import datetime
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

MODEL_NAME = "codellama:13b"
# MODEL_NAME = "deepseek-coder:6.7b"
# MODEL_NAME = "qwen2.5:3b"
model = OllamaLLM(model=MODEL_NAME)

template = """ This is a python assignment for an introductory course: {assignment}
Analyze the bugs in this python code, just mark the line numbers where the bugs are. 
Don't check syntax errors (e.g. colons, indentation, parenthesis), just the logic of the code.
Just show the top 5 bugs.
Don't repeat the same type of bug.
Don't explain anything, just show that line's text and say the name of the bug and what should be done instead.
The code might have no bugs or less than 5 bugs, in that case, just say that.
Don't consider efficiency, just the logic of the code.
Consider that the students are beginners and don't use advanced concepts.
Code (after the ---):
---
{code}
"""

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model


with open("assignment.txt", "r") as f:
    assignment = f.read()

files = os.listdir("./inputs")
for file in files:
    # get seconds in total

    if file.endswith(".txt"):
        start = datetime.datetime.now()
        with open(f"./inputs/{file}", "r") as f:
            code = f.read()
        result = chain.invoke({"assignment": assignment, "code": code})

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_file = f"./outputs/{MODEL_NAME}_{timestamp}_{file}.txt"
        with open(output_file, "w") as f:
            f.write(result)
        print(f"Result written to {output_file}")
        print(result)
        end = datetime.datetime.now()
        elapsed_time = (end - start).total_seconds()
        print(f"Elapsed time for {file}: {elapsed_time} seconds")
