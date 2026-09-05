from observability.logger import logger
from qdrant_client.models import Distance, VectorParams
from tools.utils import get_embeddings, get_qdrant_client

def _ensure_collection(my_collection: str) -> None:
    """
    Create the FAQ collection if it does not already exist.

    The embedding dimension is determined dynamically from the current
    embedding model to avoid hardcoding vector sizes.
    """

    embeddings = get_embeddings()
    qdrant_client = get_qdrant_client()

    vector_size = len(
        embeddings.embed_query("dimension-size")
    )

    collections = {
        collection.name
        for collection in qdrant_client.get_collections().collections
    }

    if my_collection not in collections:
        logger.info("Creating collection '%s'", my_collection)

        qdrant_client.create_collection(
            collection_name=my_collection,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,
            ),
        )
        return

    collection_info = qdrant_client.get_collection(my_collection)

    existing_vector_size = (
        collection_info.config.params.vectors.size
    )

    if existing_vector_size != vector_size:
        raise ValueError(
            f"""
Embedding dimension mismatch for collection '{my_collection}'.
The collection uses {existing_vector_size} dimensions
but the current embedding model uses {vector_size} dimensions.
Use an embedding model compatible with this collection
or manually create/configure a compatible collection
"""
        )
