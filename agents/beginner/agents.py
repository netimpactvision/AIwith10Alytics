import os

from crewai import Agent
from crewai.llm import LLM
from dotenv import load_dotenv

load_dotenv()

# Create an instance of OpenAI's LLM
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
llm = LLM(
    model="gpt-4o",
    temperature=0.7,
    max_tokens=4000,
    timeout=120,
)

# Define your agent with OpenAI LLM
thinker = Agent(
    role="Critical Thinker",
    goal="Analyse the text and identify if there is any conflicting information within",
    llm=llm,
    backstory=(
        "You are a critical thinker who understands details very well and expert negotiator. \
         You can identify conflicting statements, information in given text"
    ),
)