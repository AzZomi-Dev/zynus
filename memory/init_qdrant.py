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