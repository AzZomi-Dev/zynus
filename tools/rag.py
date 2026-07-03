"""
FAQ retrieval service.

This module provides semantic retrieval over frequently asked questions
stored in Qdrant. It is responsible for creating the vector collection,
loading FAQ records from the database, exposing a retriever, and serving
the retriever tool used by the researcher agent.

Responsibilities:
- Create the Qdrant collection if it does not exist.
- Build the LangChain vector store.
- Load FAQs from MySQL into Qdrant.
- Perform semantic similarity search.
- Expose a tool for the researcher agent.
"""

from database.repository import FAQRepository
from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from observability.logger import logger
from qdrant_client.models import Distance, VectorParams

from memory.qdrantClient import get_qdrant_client
from tools.utils import get_embeddings

COLLECTION_NAME = "faq"


def _ensure_collection() -> None:
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

    if COLLECTION_NAME in collections:
        return

    logger.info("Creating collection '%s'", COLLECTION_NAME)

    vector_size = len(
        embeddings.embed_query("dimension-size")
    )

    qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE,
        ),
    )


def _insert_from_db() -> int:
    """
    Load FAQ records from MySQL into Qdrant.

    Returns:
        Number of inserted FAQ documents.
    """

    repo = FAQRepository()

    faq_records = repo.get_active_faqs("en")

    docs = [
        Document(
            page_content=f"""
Question:
{faq.question}

Answer:
{faq.answer}
""",
            metadata={
                "faq_id": faq.id,
                "language": faq.language,
                "category": faq.category,
            },
        )
        for faq in faq_records
    ]

    vectorstore = _get_vectorstore()

    vectorstore.add_documents(docs)

    return len(docs)


def _get_vectorstore() -> QdrantVectorStore:
    """
    Return the FAQ vector store.

    Ensures the collection exists before constructing the vector store.
    """

    _ensure_collection()

    return QdrantVectorStore(
        client=get_qdrant_client(),
        embedding=get_embeddings(),
        collection_name=COLLECTION_NAME,
    )


def _get_retriever():
    """
    Build a semantic retriever over the FAQ collection.

    Returns:
        LangChain retriever configured for similarity search.
    """

    vectorstore = _get_vectorstore()

    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 1},
    )


def retrieve_docs(query: str):
    """
    Retrieve the most relevant FAQ documents.

    Args:
        query:
            User question.

    Returns:
        List of matching LangChain documents.
    """

    retriever = _get_retriever()

    return retriever.invoke(query)


def retriever_tool(query: str) -> list[str]:
    """
    Tool exposed to the researcher agent.

    Converts retrieved documents into plain text so they can be added
    directly to the agent's reasoning scratchpad.

    Args:
        query:
            User question.

    Returns:
        List of retrieved FAQ contents.
    """

    retrieved_docs = retrieve_docs(query)

    return [
        doc.page_content
        for doc in retrieved_docs
    ]