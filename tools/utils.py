from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from config import EMB_MODEL, EMB_MODEL_PROVIDER
import threading
import re

_emb_lock = threading.Lock()

def get_embeddings():
    if EMB_MODEL_PROVIDER == "google":
        return get_google_embeddings()
    if EMB_MODEL_PROVIDER == "huggingface":
        return get_huggingface_embeddings()

_hf_embeddings: HuggingFaceEmbeddings | None = None

def get_huggingface_embeddings():
    global _hf_embeddings

    if _hf_embeddings is not None:
        return _hf_embeddings

    with _emb_lock:
        if _hf_embeddings is not None:
            return _hf_embeddings
        
        _hf_embeddings = HuggingFaceEmbeddings(
            model_name=EMB_MODEL
        )
        return _hf_embeddings

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
    
def extract_code(code):
    pattern = r"```python3?\n(?P<code>(?:.|\n)*?)```"
    match = re.search(pattern, code)
    if match:
        return match.group(1)
    return code

def classify_failure(error: str):
    if not error:
        return "unknown"

    error = error.lower()
    if "syntaxerror" in error:
        return "SyntaxError"
    if "import" in error or "module" in error:
        return "dependency"
    if "permission" in error:
        return "security"
    return "unknown"