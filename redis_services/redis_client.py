"""
Redis client configuration.

This module creates and exposes the shared Redis client used throughout
the application for caching, rate limiting, and background job queues.
"""

from redis import Redis
from config import REDIS_URL

redis_conn = Redis.from_url(
    REDIS_URL,
    decode_responses=True
)