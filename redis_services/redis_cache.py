from redis_services.redis_client import redis_conn
from config import TTL
import hashlib

def make_cache_key(query: str):
    return f"memory:{hashlib.sha256(query.encode('utf-8')).hexdigest()}"

def get_cached_memory(query: str):
    return redis_conn.get(make_cache_key(query))

def set_memory_cache(query: str, value: str):
    redis_conn.setex(
        make_cache_key(query),
        TTL,
        value
    )