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

    collections = {
        collection.name
        for collection in qdrant_client.get_collections().collections
    }

    if my_collection in collections:
        return

    logger.info("Creating collection '%s'", my_collection)

    vector_size = len(
        embeddings.embed_query("dimension-size")
    )

    qdrant_client.create_collection(
        collection_name=my_collection,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE,
        ),
    )