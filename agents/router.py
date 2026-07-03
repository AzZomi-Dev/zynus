"""
Routing agent.

This agent determines which workflow should handle an incoming user
request. It acts as the entry point of the multi-agent system by
classifying the query into one of the supported execution paths.

Supported routes:
- qa: General question answering.
- research: Tool-assisted research.
- code: Code generation and execution.

Responsibilities:
- Analyze the user's query.
- Select the appropriate workflow.
- Validate the returned route.
- Fallback to a safe default for invalid responses.
"""

from agents.llm import ask_llm_json
from schemas.router_schema import RouterResponse


def router_agent(query: str) -> str:
    """
    Classify the user's query into the appropriate workflow.

    The router asks the language model to choose the most suitable
    processing route, validates the structured response, and falls
    back to the QA workflow if an invalid route is returned.

    Args:
        query:
            User input.

    Returns:
        One of:
        - "qa"
        - "research"
        - "code"
    """

    prompt = f"""
You are a router agent.

Choose the best route based on the query type.

Routes:

- qa
  General question answering.

- research
  Questions requiring external information or tool usage.

- code
  Requests involving writing or modifying code.

Return only valid JSON.

Example:
{{
    "route": "qa"
}}

The query is:
{query}
"""

    response = ask_llm_json(prompt)

    parsed = RouterResponse(**response)

    allowed_routes = {
        "qa",
        "research",
        "code",
    }

    # Defensive validation in case the LLM returns an unexpected route.
    if parsed.route not in allowed_routes:
        return "qa"

    return parsed.route