"""
Memory retrieval agent.

This agent retrieves relevant semantic memories for a given query while
using Redis as a cache to minimize repeated vector database searches.

Retrieval flow:
1. Check Redis cache.
2. If cached, return immediately.
3. Otherwise, query Qdrant.
4. Format retrieved memories.
5. Cache the formatted result.
6. Return the formatted context.

Responsibilities:
- Coordinate memory retrieval.
- Utilize Redis caching.
- Format memories for prompt injection.
"""

from memory.memory_retriever import retrieve_memory
from redis_services.redis_cache import (
    get_cached_memory,
    set_memory_cache,
)


def memory_agent(query: str) -> tuple[str, bool]:
    """
    Retrieve relevant semantic memories for a query.

    The returned context is intended to be injected directly into LLM
    prompts to improve code generation using previous successful
    solutions.

    Args:
        query:
            User task or question.

    Returns:
        A tuple containing:
        - Formatted memory context.
        - True if served from Redis cache, otherwise False.
    """

    # Attempt to serve from Redis cache first.
    cached = get_cached_memory(query)

    if cached:
        return cached, True

    # Cache miss: perform semantic search.
    points = retrieve_memory(query)

    docs = []

    for point in points:
        docs.append(
            f"""
Query: {point.payload["query"]}
Its solution: {point.payload["solution"]}
"""
        )

    result = "\n\n".join(docs)

    # Cache successful retrievals.
    if result:
        set_memory_cache(query, result)

    return result, False