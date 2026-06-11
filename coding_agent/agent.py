from google.adk.agents import LoopAgent, SequentialAgent, Agent
from dotenv import load_dotenv
from google.adk.models.lite_llm import LiteLlm

MODEL = LiteLlm("openai/gpt-4o-mini")

load_dotenv()

from .subagents.code_generator import initial_code_generator
from .subagents.code_refiner import code_refiner  
from .subagents.code_tester import code_tester

################################################
from langfuse import get_client

langfuse = get_client()

# Verify connection
if langfuse.auth_check():
    print("Langfuse client is authenticated and ready!")
else:
    print("Authentication failed. Please check your credentials and host.")

from openinference.instrumentation.google_adk import GoogleADKInstrumentor

GoogleADKInstrumentor().instrument()

##################################################

improvement_loop = LoopAgent(
    name="improvement_loop",
    description="Iteratively reviews and refines the generated code until quality requirements are met",
    sub_agents=[code_tester, code_refiner],
    max_iterations=5,
)


coding_agent = SequentialAgent(
    name="coding_agent",
    description="Generates and refines the code through an iterative review process",
    sub_agents=[initial_code_generator, improvement_loop],
)

root_agent = Agent(
    name="delegator_agent",
    model=MODEL,
    instruction="""
    You are a Delegator Agent responsible for orchestrating the code generation and refinement process.
    When the user provides a coding task, delegate the task to the coding agent.
    When the user provides other types of input, respond politely and await further instructions without executing any tools.
    """,
    description="Orchestrates the code generation and refinement process",
    sub_agents=[coding_agent],
    )
    