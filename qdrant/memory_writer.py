from langchain_core.documents import Document
from qdrant.vectorstore import _get_vectorstore

# docs

def _insert_memory(record: dict, trace_id: str) -> None:
    """
    Store a successful execution record.
    Enabling future semantic searches over previously solved tasks.

    Args:
        record:
            Memory record containing the query, solution, and metadata.
        trace_id:
            Unique ID
    """

    text = f"""
The query:
{record["query"]}

Its solution:
{record["solution"]}
""".strip()
    
    docs = [
        Document(
            page_content=text,
            metadata={
                "id": trace_id,
                "query": record["query"],
                "solution": record["solution"],
                "failure_type": record["failure_type"],
                "retries": record["retries"]
            }
        )
    ]
    vectorstore = _get_vectorstore("memory")
    vectorstore.add_documents(docs)
    return len(docs)