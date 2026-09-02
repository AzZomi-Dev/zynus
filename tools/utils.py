from providers.embeddings.hf import get_huggingface_embeddings
from providers.embeddings.google import get_google_embeddings
from config import EMB_MODEL_PROVIDER, QDRANT_URL, QDRANT_API_KEY
from qdrant_client import QdrantClient
import threading
import re

qdrant_client: QdrantClient | None = None
_client_lock = threading.Lock()

def get_qdrant_client() -> QdrantClient:
    global qdrant_client

    if qdrant_client is not None:
        return qdrant_client

    with _client_lock:

        if qdrant_client is not None:
            return qdrant_client

        qdrant_client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY or None
        )

        return qdrant_client

def get_embeddings():
    if EMB_MODEL_PROVIDER == "google":
        return get_google_embeddings()
    if EMB_MODEL_PROVIDER == "huggingface":
        return get_huggingface_embeddings()
    
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