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
    1. Use the execute_code tool to run the source code provided in `{generated_code}`.
    2. Analyze the tool execution output for any syntax errors, runtime exceptions, or bugs.

    ## OUTPUT INSTRUCTIONS
    IF the code execution fails or produces an error:
    - Return the exact error log and traceback message as feedback. Do not add conversational fluff.

    ELSE IF the code runs successfully with zero errors:
    - Call the exit_loop function.
    - Return "Code executed successfully with no errors. Exiting the refinement loop."

    ## CODE TO TEST
    {generated_code}
    """,

    description="Executes code to isolate runtime errors, providing raw tracebacks on failure or breaking the loop on success.",
    tools=[execute_code, exit_loop],
    output_key="test_feedback",
)