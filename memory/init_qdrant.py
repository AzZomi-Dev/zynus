"""
Initialize the Qdrant memory collection.

This script recreates the "memory" collection using the current
embedding model's vector dimension.

Warning:
Running this script deletes the existing collection and all stored
vectors. It is intended for local development, testing, or resetting
the vector database.
"""
from memory.qdrantClient import get_qdrant_client
from qdrant_client.models import VectorParams, Distance
from tools.utils import get_embeddings

embeddings = get_embeddings()
vector_size = len(embeddings.embed_query("dimenstion-check"))
qdrant_client = get_qdrant_client()

qdrant_client.recreate_collection(
    collection_name="memory",
    vectors_config=VectorParams(
        size=vector_size,
        distance=Distance.COSINE
    )
)