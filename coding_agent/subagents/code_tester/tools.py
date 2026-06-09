"""
Tools for Code Tester Agent

This module provides tools for executing and validating generated source code.
"""

import docker
from docker.errors import ContainerError, APIError
from typing import Any, Dict
from google.adk.tools.tool_context import ToolContext

def execute_code(code: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Executes Python code safely inside an isolated local Docker container.
    Prevents host file damage, infinite loops, and unauthorized network calls.

    Args:
        code: The Python source code string to execute.
        tool_context: Context for accessing and updating session state.
    """
    # Clean up markdown block wrapping if present
    if "```python" in code:
        code = code.split("```python")[1].split("```")[0].strip()
    elif "```" in code:
        code = code.split("```")[1].split("```")[0].strip()

    print("\n----------- DOCKER SANDBOX EXECUTION -----------")
    print("Provisioning ephemeral container workspace...")
    print("------------------------------------------------\n")

    # Connect to the local Docker Desktop daemon
    try:
        client = docker.from_env()
    except Exception as e:
        return {
            "result": "fail",
            "output": "",
            "error": f"Failed to connect to Docker Desktop. Ensure it is running. Error: {str(e)}",
            "message": "Docker infrastructure failure."
        }

    container = None
    TIMEOUT_SECONDS = 10  # Hard stop for malicious or broken infinite loops

    try:
        # Create the container configuration
        container = client.containers.create(
            image="python:3.11-slim",
            command=["python", "-c", code],
            network_disabled=True,        # CRITICAL: Disables outbound/inbound internet access
            mem_limit="256m",             # CRITICAL: Restricts memory to prevent RAM exhaustion
            nano_cpus=1000000000,         # CRITICAL: Restricts execution to 1 CPU core max
        )

        # Fire up the container
        container.start()

        # Monitor container execution status with a strict timeout constraint
        result = container.wait(timeout=TIMEOUT_SECONDS)
        exit_code = result.get("StatusCode", -1)
        
        # Grab the container console output logs
        captured_logs = container.logs(stdout=True, stderr=True).decode("utf-8")

        if exit_code == 0:
            tool_context.state["test_status"] = "pass"
            return {
                "result": "pass",
                "output": captured_logs,
                "message": "Code executed successfully inside Docker sandbox with zero errors.",
            }
        else:
            tool_context.state["test_status"] = "fail"
            return {
                "result": "fail",
                "output": captured_logs,
                "error": f"Runtime exit code {exit_code}",
                "message": "The script compiled but threw an execution runtime error.",
            }

    except ConnectionError:
        tool_context.state["test_status"] = "fail"
        return {
            "result": "fail",
            "output": "",
            "error": f"Execution timed out! The script took longer than {TIMEOUT_SECONDS}s to finish.",
            "message": "Potential infinite loop detected and terminated.",
        }
    except APIError as e:
        tool_context.state["test_status"] = "fail"
        return {
            "result": "fail",
            "output": "",
            "error": str(e),
            "message": "Docker Engine API failure encountered.",
        }
    finally:
        # Defensive cleanup: Always wipe the container instance completely off the host machine
        if container:
            try:
                container.remove(force=True)
            except Exception:
                pass

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