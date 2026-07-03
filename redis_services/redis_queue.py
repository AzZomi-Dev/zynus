"""
Redis queue configuration.

This module exposes the shared RQ queue used for asynchronous memory
persistence tasks. The queue is reused throughout the application to
enqueue background jobs.
"""

from rq import Queue
from redis_services.redis_client import redis_conn

memory_write_queue = Queue(
    "memory-write",
    connection=redis_conn
)