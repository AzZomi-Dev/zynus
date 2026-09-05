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

from qdrant.vectorstore import _get_vectorstore

def _get_retriever(my_collection: str):
    """
    Build a semantic retriever over the given collection.

    Returns:
        LangChain retriever configured for similarity search.
    """

    vectorstore = _get_vectorstore(my_collection)

    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 1},
    )

def retriever_tool(query: str, my_collection: str) -> list[str]:
    """
    Tool exposed to the researcher agent.

    Converts retrieved documents into plain text so they can be added
    directly to the agent's reasoning scratchpad.

    Args:
        query:
            User question.

    Returns:
        List of retrieved collection contents.
    """

    retriever = _get_retriever(my_collection)
    retrieved_docs = retriever.invoke(query)

    return [
        doc.page_content
        for doc in retrieved_docs
    ]