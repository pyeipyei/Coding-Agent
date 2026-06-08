from google.adk.agents import LoopAgent, SequentialAgent
from dotenv import load_dotenv

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


root_agent = SequentialAgent(
    name="coding_agent",
    description="Generates and refines the code through an iterative review process",
    sub_agents=[initial_code_generator, improvement_loop],
)