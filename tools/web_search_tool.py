"""
Web search tool.

This module provides a simple wrapper around DuckDuckGo Search for the
research agent. It retrieves relevant web results and converts them into
a normalized format that can be consumed by the agent.

Responsibilities:
- Execute web searches.
- Normalize search results.
- Handle search failures gracefully.
"""

from ddgs import DDGS

def web_search_tool(query: str) -> list[dict] | str:
    """
    Search the web using DuckDuckGo.

    Args:
        query:
            Search query.

    Returns:
        On success:
            A list of search results, where each result contains:
            - title
            - snippet
            - url

        On failure:
            A human-readable error message that can be consumed by the
            researcher agent.
    """

    results = []

    try:
        with DDGS() as ddgs:
            for result in ddgs.text(query, max_results=5):
                results.append(
                    {
                        "title": result.get("title"),
                        "snippet": result.get("body"),
                        "url": result.get("href"),
                    }
                )

        return results

    except Exception as e:
        return (
            f"Web search tool has an error: {e}. "
            "Try another tool."
        )