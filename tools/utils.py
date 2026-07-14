from providers.embeddings.hf import get_huggingface_embeddings
from providers.embeddings.google import get_google_embeddings
from config import EMB_MODEL_PROVIDER
import re

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