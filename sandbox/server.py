"""
Sandbox service.

This service executes Python code inside an isolated environment and
returns the captured standard output and standard error.

Responsibilities:
- Receive execution requests.
- Execute Python code with a timeout.
- Capture stdout and stderr.
- Clean up temporary files.
"""

import os
import subprocess
import tempfile

from fastapi import FastAPI

app = FastAPI(title="zynus", version="1.0.6")


async def execute_code(code: str) -> dict:
    """
    Execute Python code in a temporary file.

    The source code is written to a temporary file, executed in a
    separate process, and removed after execution completes.

    Args:
        code:
            Python source code.

    Returns:
        Dictionary containing:
        - stdout
        - stderr
    """

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".py",
            mode="w",
            delete=False,
            encoding="utf-8",
        ) as file:
            file.write(code)
            temp_path = file.name

        result = subprocess.run(
            ["python", temp_path],
            capture_output=True,
            text=True,
            timeout=10,
        )

        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": "Execution timed out",
        }

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@app.get("/")
async def home():
    """
    Health endpoint for the sandbox service.
    """

    return {
        "message": "zynus-sandbox is running",
    }


@app.post("/execute")
async def execute(payload: dict):
    """
    Execute submitted Python code.

    Args:
        payload:
            Request body containing the "code" field.

    Returns:
        Execution result produced by the sandbox.
    """

    return await execute_code(payload["code"])