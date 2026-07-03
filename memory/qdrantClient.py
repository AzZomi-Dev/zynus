"""
Qdrant client provider.

This module exposes a lazily initialized, thread-safe singleton instance
of the Qdrant client. Reusing a single client avoids repeatedly creating
connections and provides efficient access across the application.

Responsibilities:
- Lazily create the Qdrant client.
- Ensure thread-safe initialization.
- Reuse a single client instance.
"""

import threading

from qdrant_client import QdrantClient

from config import QDRANT_URL

qdrant_client: QdrantClient | None = None
_client_lock = threading.Lock()


def get_qdrant_client() -> QdrantClient:
    """
    Return the shared Qdrant client instance.

    The client is created only once using double-checked locking to
    ensure safe initialization when accessed concurrently.

    Returns:
        Shared Qdrant client.
    """

    global qdrant_client

    if qdrant_client is not None:
        return qdrant_client

    with _client_lock:

        if qdrant_client is not None:
            return qdrant_client

        qdrant_client = QdrantClient(url=QDRANT_URL)

        return qdrant_client