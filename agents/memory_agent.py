"""
Memory retrieval agent.

This agent retrieves relevant semantic memories for a given query while
using Redis as a cache to minimize repeated vector database searches.

Retrieval flow:
1. Check Redis cache.
2. If cached, return immediately.
3. Otherwise, query Qdrant.
5. Cache the retrieved memories if any.
6. Return the retrieved memories.

Responsibilities:
- Coordinate memory retrieval.
- Utilize Redis caching.
- Retrieve memories for prompt injection.
"""

from tools.rag import retriever_tool
from redis_services.redis_cache import (
    get_cached_memory,
    set_memory_cache,
)


def memory_agent(query: str) -> tuple[str, bool]:
    """
    Retrieve relevant semantic memories for a query.

    The returned context is intended to be injected directly into LLM
    prompts to improve the generation using previous successful
    solutions.

    Args:
        query:
            User task or question.

    Returns:
        A tuple containing:
        - Memory.
        - True if served from Redis cache, otherwise False.
    """

    cached = get_cached_memory(query)
    if cached:
        return cached, True

    memory_docs = retriever_tool(query, "memory")
    if memory_docs:
        memory = "\n\n".join(memory_docs)
        set_memory_cache(query, memory)

    return memory, False