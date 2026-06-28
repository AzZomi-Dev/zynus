from tools.utils import get_embeddings
from memory.qdrantClient import get_qdrant_client

def embed_and_upsert_memory(query: str, trace_id: str):
    embeddings = get_embeddings()
    vector = embeddings.embed_query(query)
    qdrant_client = get_qdrant_client()

    qdrant_client.upsert(
        collection_name="memory",
        points=[{
            "id": trace_id,
            "vector": vector,
            "payload": {
                "query": query
            }
        }]
    )