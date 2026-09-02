from langchain_qdrant import QdrantVectorStore

from tools.utils import get_embeddings, get_qdrant_client
from qdrant.ensure_collection import _ensure_collection

def _get_vectorstore(my_collection: str) -> QdrantVectorStore:
    """
    Return the vector store.

    Ensures the collection exists before constructing the vector store.
    """

    _ensure_collection(my_collection)

    return QdrantVectorStore(
        client=get_qdrant_client(),
        embedding=get_embeddings(),
        collection_name=my_collection,
    )
