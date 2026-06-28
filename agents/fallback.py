def fallback_agent(
        query: str,
        error: str,
        feedback: str,
        retries: int,
        trace_id: str
    ):

    return f"""
SYSTEM FAILURE REPORT

All '{retries}' retries consumed without solution

Query ID: {trace_id}
Query: {query}
Error: {error}
Feedback: {feedback}
"""