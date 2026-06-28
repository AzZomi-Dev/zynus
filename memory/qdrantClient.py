from qdrant_client import QdrantClient
from config import QDRANT_URL
import threading

qdrant_client: QdrantClient | None = None
_client_lock = threading.Lock()

def get_qdrant_client():
    global qdrant_client

    if qdrant_client is not None:
        return qdrant_client
    
    with _client_lock:
        if qdrant_client is not None:
            return qdrant_client
        
        qdrant_client = QdrantClient(url=QDRANT_URL)
        return qdrant_client