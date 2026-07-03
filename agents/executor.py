"""
Sandbox execution agent.

This agent is responsible for executing generated Python code inside an
isolated sandbox environment. The sandbox protects the host application
from running untrusted code.

Responsibilities:
- Send generated code to the sandbox service.
- Capture standard output and standard error.
- Handle communication failures gracefully.
- Return execution results to the workflow.
"""

import requests

from config import SANDBOX_URL


def executor_agent(code: str) -> tuple[str, str]:
    """
    Execute generated Python code in the sandbox.

    The sandbox is exposed as an HTTP service and returns the execution
    result as JSON containing stdout and stderr.

    Args:
        code:
            Python source code to execute.

    Returns:
        A tuple containing:
        - stdout: Program output.
        - stderr: Runtime or execution errors.
    """

    try:
        payload = {"code": code}

        response = requests.post(
            SANDBOX_URL,
            json=payload,
            timeout=15,
        )

        response.raise_for_status()

        result = response.json()

        stdout = result["stdout"]
        stderr = result["stderr"]

        return stdout, stderr

    except Exception as e:
        return "", f"Execution error: {e}"