from memory.qdrantClient import get_qdrant_client
from qdrant_client import models
from qdrant_client.models import Filter
from tools.utils import get_embeddings

def retrieve_memory(query: str, limit: int = 1):
    qdrant_client = get_qdrant_client()

    embeddings = get_embeddings()
    vector = embeddings.embed_query(query)

    results = qdrant_client.query_points(
        collection_name="memory",
        query=vector,
        limit=limit
    )
    return results.points