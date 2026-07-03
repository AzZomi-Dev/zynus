"""
Memory cache service.

This module provides helper functions for caching retrieved semantic
memories in Redis. Cache keys are generated from a SHA-256 hash of the
query to produce deterministic, fixed-length keys.

Responsibilities:
- Generate cache keys.
- Retrieve cached memories.
- Store memories with a configurable TTL.
"""

from redis_services.redis_client import redis_conn
from config import TTL
import hashlib

def make_cache_key(query: str):
    """
    Generate a deterministic Redis cache key for a query.

    Args:
        query:
            User query.

    Returns:
        SHA-256 based cache key.
    """
    return f"memory:{hashlib.sha256(query.encode('utf-8')).hexdigest()}"

def get_cached_memory(query: str):
    """
    Retrieve cached memory for a query.

    Args:
        query:
            User query.

    Returns:
        Cached memory if present, otherwise None.
    """
    return redis_conn.get(make_cache_key(query))

def set_memory_cache(query: str, value: str):
    """
    Cache retrieved memory with a time-to-live (TTL).

    Args:
        query:
            User query.

        value:
            Formatted memory to cache.
    """
    redis_conn.setex(
        make_cache_key(query),
        TTL,
        value
    )