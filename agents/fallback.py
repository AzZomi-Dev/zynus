"""
Fallback agent.

This agent generates the final response when the workflow cannot produce
a successful solution after exhausting all retry attempts.

Its purpose is to provide a concise diagnostic report containing enough
information for debugging while ensuring the workflow always returns a
meaningful response.
"""


def fallback_agent(
    query: str,
    error: str,
    feedback: str,
    retries: int,
    trace_id: str,
) -> str:
    """
    Build the final failure report.

    Args:
        query:
            Original user request.

        error:
            Last execution error reported by the sandbox.

        feedback:
            Final feedback from the critic agent.

        retries:
            Total number of retry attempts performed.

        trace_id:
            Unique request identifier used for log correlation.

    Returns:
        Human-readable failure report.
    """

    return f"""
SYSTEM FAILURE REPORT

All '{retries}' retries consumed without solution

Query ID: {trace_id}
Query: {query}
Error: {error}
Feedback: {feedback}
"""