"""
Memory retrieval service.

This module performs semantic similarity searches against the Qdrant
memory collection. It converts user queries into embeddings and returns
the most relevant stored memories.

Responsibilities:
- Generate query embeddings.
- Perform vector similarity search.
- Return matching memory records.
"""

from qdrant_client.models import Filter

from memory.qdrantClient import get_qdrant_client
from tools.utils import get_embeddings


def retrieve_memory(query: str, limit: int = 1):
    """
    Retrieve the most semantically similar memories.

    Args:
        query:
            User query used for semantic search.

        limit:
            Maximum number of matching memories to return.

    Returns:
        List of Qdrant search results ordered by similarity.
    """

    qdrant_client = get_qdrant_client()

    embeddings = get_embeddings()
    vector = embeddings.embed_query(query)

    results = qdrant_client.query_points(
        collection_name="memory",
        query=vector,
        limit=limit,
    )

    return results.points