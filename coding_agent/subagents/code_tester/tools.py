"""
Tools for Code Tester Agent

This module provides tools for executing and validating generated source code.
"""

import sys
import traceback
from io import StringIO
from typing import Any, Dict

from google.adk.tools.tool_context import ToolContext


def execute_code(code: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Tool to execute Python code in an isolated environment and capture runtime feedback.
    Updates test_status in the state based on execution success.

    Args:
        code: The Python source code string to execute
        tool_context: Context for accessing and updating session state

    Returns:
        Dict[str, Any]: Dictionary containing:
            - result: 'fail' or 'pass'
            - output: Standard output captured during execution
            - error: Full traceback string if an exception occurred
            - message: Summary feedback message
    """
    # Defensive parsing: strip markdown code blocks if present
    if "```python" in code:
        code = code.split("```python")[1].split("```")[0].strip()
    elif "```" in code:
        code = code.split("```")[1].split("```")[0].strip()

    print("\n----------- TOOL DEBUG -----------")
    print("Executing generated code workspace...")
    print("----------------------------------\n")

    # Capture standard output
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()

    try:
        # Execute code in a clean global context
        execution_globals = {"__builtins__": __builtins__}
        exec(code, execution_globals)
        
        # Restore stdout and fetch logs
        sys.stdout = old_stdout
        captured_output = redirected_output.getvalue()

        tool_context.state["test_status"] = "pass"
        return {
            "result": "pass",
            "output": captured_output,
            "message": "Code executed successfully with zero runtime errors.",
        }

    except Exception as e:
        # Restore stdout and capture traceback details
        sys.stdout = old_stdout
        captured_output = redirected_output.getvalue()
        error_traceback = traceback.format_exc()

        tool_context.state["test_status"] = "fail"
        return {
            "result": "fail",
            "output": captured_output,
            "error": error_traceback,
            "message": f"Runtime Error encountered: {str(e)}",
        }


def exit_loop(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Call this function ONLY when the code passes all execution and quality requirements,
    signaling the iterative refinement process should end.

    Args:
        tool_context: Context for tool execution

    Returns:
        Empty dictionary
    """
    print("\n----------- EXIT LOOP TRIGGERED -----------")
    print("Code verification completed successfully")
    print("Loop will exit now")
    print("------------------------------------------\n")

    tool_context.actions.escalate = True
    return {}