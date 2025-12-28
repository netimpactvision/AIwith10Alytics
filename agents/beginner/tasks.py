from crewai import Task

from agents import thinker

# Define a task with a description and expected output
conflict_task = Task(
    description=(
        "Find if there are any conflicting statement / information in text. \n Text : \n{text}"
    ),
    expected_output="Respond with 'There are no conflicts' / 'There is a conflict'",
    agent=thinker,
)
