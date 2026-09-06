"""
Code evaluation (critic) agent.

This agent evaluates the outcome of generated code execution and determines
whether the workflow should succeed or continue with another repair attempt.

Evaluation strategy:
1. If the sandbox reports a runtime error, immediately fail with the error.
2. Otherwise, ask the LLM to review the generated code.
3. Parse the LLM's structured JSON response.
4. Return a success flag and concise feedback.

Responsibilities:
- Evaluate execution results.
- Produce feedback for the repair agent.
- Support deterministic testing through DEBUG_MODE.
"""

from agents.llm import ask_llm_json
from config import DEBUG_MODE, MODE
from schemas.critic_schema import CriticResponse
from pydantic import ValidationError
from observability.logger import logger

def critic_agent(
    query: str,
    code: str,
    error: str,
    retries: int,
) -> tuple[bool, str]:
    """
    Evaluate the generated code.

    The critic decides whether the current execution satisfies the user's
    request or whether another repair iteration is required.

    During development, DEBUG_MODE returns deterministic responses to
    simplify workflow testing without invoking the LLM.

    Args:
        query:
            Original user request.

        code:
            Generated Python code.

        error:
            Runtime error returned by the sandbox, if any.

        retries:
            Current retry attempt.

    Returns:
        A tuple containing:
        - success: True if execution is acceptable.
        - feedback: Explanation used by the repair agent.
    """

    # Development shortcut for deterministic testing.
    if DEBUG_MODE:

        if MODE == "fixed":
            if retries == 0:
                return False, "Fail feedback test"

            if retries == 1:
                return True, "Success feedback test"

        if MODE == "fall":
            return False, error

    # Runtime errors always require another repair attempt.
    if error.strip():
        return False, f"Error: {error}"

    prompt = f"""
You are an evaluator.

The task was:
{query}

Generated code:
{code}

Return only valid JSON.

Example:
{{
    "success": true,
    "feedback": "Why"
}}

Be strict and concise.
"""
    for _ in range(3):

        response = ask_llm_json(prompt)
        try:
            parsed = CriticResponse(**response)
            return parsed.success, parsed.feedback
        except ValidationError as e:
            logger.warning("Invalid critic response. Retrying: %s",e)
            continue
    return False, "Critic failed to return a valid response."