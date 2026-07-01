from redis import Redis
from config import REDIS_URL

redis_conn = Redis.from_url(
    REDIS_URL,
    decode_responses=True
)