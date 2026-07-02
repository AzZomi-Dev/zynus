from tools.utils import get_embeddings
from memory.qdrantClient import get_qdrant_client
from observability.logger import logger
from qdrant_client.models import VectorParams, Distance
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document
from database.repository import FAQRepository

COLLECTION_NAME = "faq"

def _ensure_collection():
    embeddings = get_embeddings()
    qdrant_client = get_qdrant_client()

    collections = {
        c.name
        for c in qdrant_client.get_collections().collections
    }
    if COLLECTION_NAME in collections:
        return
    
    logger.info("Creating collection '%s'", COLLECTION_NAME)
    vector_size = len(embeddings.embed_query("dimension-size"))

    qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE
        )
    )

def _insert_from_db():

    repo = FAQRepository()
    faq_records = repo.get_active_faqs("en")

    docs = [Document(
        page_content=f""""
Question:
{faq.question}

Answer:
{faq.answer}
""",
        metadata={
            "faq_id": faq.id,
            "language": faq.language,
            "category": faq.category
        }
    ) for faq in faq_records]
    vectorstore = _get_vectorstore()
    vectorstore.add_documents(docs)
    return len(docs)

def _get_vectorstore():

    _ensure_collection()

    return QdrantVectorStore(
        client=get_qdrant_client(),
        embedding=get_embeddings(),
        collection_name=COLLECTION_NAME
    )

def _get_retriever():
    vectorstore = _get_vectorstore()
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 1}
    )
    return retriever

def retrieve_docs(query: str):
    retriever = _get_retriever()
    docs = retriever.invoke(query)
    return docs

def retriever_tool(query: str):
    
    retrieved_docs = retrieve_docs(query)
    documents = []
    
    for doc in retrieved_docs:
        documents.append(doc.page_content)
        
    return documents