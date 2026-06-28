from config import SANDBOX_URL
import requests

def executor_agent(code: str):

    try:
        payload = {"code": code}
        response = requests.post(
            SANDBOX_URL,
            json=payload,
            timeout=15
        )

        result = response.json()

        stdout = result["stdout"]
        stderr = result["stderr"]

        return stdout, stderr

    except Exception as e:
        return "", f"Execution error: {e}"