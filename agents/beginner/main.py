"""
CrewAI Memory Docs: https://docs.crewai.com/en/concepts/memory
"""

import os

from crewai import Crew

from agents import thinker
from tasks import conflict_task

# "/Users/ishandutta/Documents/code/outskill/agents/beginner/crewai_memory"
os.environ["CREWAI_STORAGE_DIR"] = (
    "/crewai_memory"
)

# Define the Crew with agents and tasks
crew = Crew(
    agents=[thinker],
    tasks=[conflict_task],
    memory=True,
)

# Kickoff the Crew with the input query
# Text = "After a long day at office, I was going back home in the late evening. Then, I met my friend on the way to office."
# Text = "I love to travel to new places and explore the culture and food of the place."
# Text = "I went to the library to study, but I forgot to bring my books and studied all of them."
# Text = "She said she has never been to Paris, yet she described the Eiffel Tower in great detail from her last trip."
Text = "Ghana records over 334,000 HIV patients in 2025, Accra ranked highest"

result = crew.kickoff(inputs={"text": Text})

print("Answer:", result)
