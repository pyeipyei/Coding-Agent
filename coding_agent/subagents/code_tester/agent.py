from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from .tools import execute_code, exit_loop

MODEL = LiteLlm("openai/gpt-4o-mini")

code_tester = Agent(
    name="CodeTester",
    model=MODEL,
    instruction="""You are an automated Code Tester operating in a development pipeline.

    Your task is to run and evaluate the correctness of the generated code.

    ## EVALUATION PROCESS
    1. You MUST ALWAYS call the execute_code tool first using the source code provided in the "CODE TO TEST" section below. Do not assume it works without executing it.
    2. Analyze the tool execution output from execute_code for any syntax errors, runtime exceptions, or bugs.

    ## CONVERSATIONAL FALLBACK
    If the user's latest message is a casual greeting, conversational question, or instruction to write code (rather than providing code to test), do not run any code. Immediately execute the `exit_loop` function, respond politely, and await further instructions.

    ## OUTPUT INSTRUCTIONS
    - IF the execute_code tool returns a failure, error log, or traceback: Return the exact error log and traceback message as feedback. Do not add conversational fluff.
    - IF the execute_code tool completes successfully with zero errors: Call the exit_loop function and return "Code executed successfully with no errors. Exiting the refinement loop."

    ## CODE TO TEST
    {generated_code}
    """,

    description="Executes code to isolate runtime errors, providing raw tracebacks on failure or breaking the loop on success.",
    tools=[execute_code, exit_loop],
    output_key="test_feedback",
)