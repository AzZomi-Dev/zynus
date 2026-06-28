from langchain_huggingface import HuggingFaceEmbeddings
from config import EMB_MODEL
import threading
import re

_embeddings: HuggingFaceEmbeddings | None = None
_emb_lock = threading.Lock()

def get_embeddings():
    global _embeddings

    if _embeddings is not None:
        return _embeddings

    with _emb_lock:
        if _embeddings is not None:
            return _embeddings
        
        _embeddings = HuggingFaceEmbeddings(
            model_name=EMB_MODEL,
            model_kwargs={"local_files_only": True}
        )
        return _embeddings
    
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