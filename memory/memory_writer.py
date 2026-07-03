"""
Memory indexing service.

This module converts successful execution records into vector embeddings
and stores them in the Qdrant memory collection for future semantic
retrieval.

Responsibilities:
- Build the embedding text.
- Generate vector embeddings.
- Upsert memory records into Qdrant.
"""

from memory.qdrantClient import get_qdrant_client
from tools.utils import get_embeddings

COLLECTION_NAME = "memory"


def embed_and_upsert_memory(record: dict, trace_id: str) -> None:
    """
    Embed and store a successful execution record.

    The generated embedding combines the original query and its solution,
    enabling future semantic searches over previously solved tasks.

    Args:
        record:
            Memory record containing the query, solution, and metadata.

        trace_id:
            Unique identifier used as the vector ID.
    """

    text = f"""
The query:
{record["query"]}

Its solution:
{record["solution"]}
""".strip()

    embeddings = get_embeddings()
    vector = embeddings.embed_query(text)

    qdrant_client = get_qdrant_client()

    qdrant_client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            {
                "id": trace_id,
                "vector": vector,
                "payload": {
                    "id": trace_id,
                    "query": record["query"],
                    "solution": record["solution"],
                    "failure_type": record["failure_type"],
                    "retries": record["retries"],
                },
            }
        ],
    )