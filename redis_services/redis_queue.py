from rq import Queue
from redis_services.redis_client import redis_conn

memory_write_queue = Queue(
    "memory-write",
    connection=redis_conn
)