from database.repository import FAQRepository
from langchain_core.documents import Document
from qdrant.vectorstore import _get_vectorstore

def _insert_faq(my_collection: str) -> int:
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

    vectorstore = _get_vectorstore(my_collection)
    vectorstore.add_documents(docs)

    return len(docs)
