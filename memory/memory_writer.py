from tools.utils import get_embeddings
from memory.qdrantClient import get_qdrant_client

def embed_and_upsert_memory(record: dict, trace_id: str):

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
        collection_name="memory",
        points=[{
            "id": trace_id,
            "vector": vector,
            "payload": {
                "id": trace_id,
                "query": record["query"],
                "solution": record["solution"],
                "failure_type": record["failure_type"],
                "retries": record["retries"]
            }
        }]
    )