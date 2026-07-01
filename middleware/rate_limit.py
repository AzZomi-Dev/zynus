from redis_services.redis_client import redis_conn
from config import REQUESTS_WINDOW, REQUESTS_LIMIT
from fastapi import Request, HTTPException

def rate_limit_dependency(request: Request):    
    identifier = request.client.host

    if not allow_request(identifier):
        raise HTTPException(
            status_code=429,
            detail="Too many requests"
        )

def allow_request(identifier: str) -> bool:
    key = f"rate:{identifier}"

    current = redis_conn.incr(key)
    if current == 1:
        redis_conn.expire(key, REQUESTS_WINDOW)

    return current <= REQUESTS_LIMIT