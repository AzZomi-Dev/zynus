"""
Rate limiting middleware.

This module implements a Redis-backed fixed-window rate limiter for the
API. Each client is identified by its IP address, and requests exceeding
the configured limit within the time window are rejected.

Responsibilities:
- Enforce API rate limits.
- Track request counts in Redis.
- Reject excessive requests with HTTP 429.
"""

from redis_services.redis_client import redis_conn
from config import REQUESTS_WINDOW, REQUESTS_LIMIT
from fastapi import Request, HTTPException

def rate_limit_dependency(request: Request):    
    """
    Enforce rate limiting for an incoming request.

    Args:
        request:
            Incoming FastAPI request.

    Raises:
        HTTPException:
            If the client exceeds the configured request limit.
    """
    identifier = request.client.host

    if not allow_request(identifier):
        raise HTTPException(
            status_code=429,
            detail="Too many requests"
        )

def allow_request(identifier: str) -> bool:
    """
    Determine whether a client is allowed to make another request.

    Args:
        identifier:
            Unique client identifier (typically the client IP address).

    Returns:
        True if the request is allowed, otherwise False.
    """
    key = f"rate:{identifier}"

    current = redis_conn.incr(key)
    if current == 1:
        redis_conn.expire(key, REQUESTS_WINDOW)

    return current <= REQUESTS_LIMIT