from langchain_google_genai import GoogleGenerativeAIEmbeddings
from config import EMB_MODEL
import threading

_emb_lock = threading.Lock()
_google_embeddings: GoogleGenerativeAIEmbeddings | None = None

def get_google_embeddings():
    global _google_embeddings

    if _google_embeddings is not None:
        return _google_embeddings

    with _emb_lock:
        if _google_embeddings is not None:
            return _google_embeddings
        
        _google_embeddings = GoogleGenerativeAIEmbeddings(
            model=EMB_MODEL
        )
        return _google_embeddings
