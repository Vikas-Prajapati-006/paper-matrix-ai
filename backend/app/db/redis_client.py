import redis
from app.core.config import settings
from app.core.logger import logger

redis_pool = redis.ConnectionPool.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    socket_timeout=5,
    socket_connect_timeout=5,
)


def get_redis_client() -> redis.Redis:
    """Returns a Redis client instance from the shared connection pool."""
    return redis.Redis(connection_pool=redis_pool)


def check_redis_health() -> bool:
    """Checks if Redis instance is active and reachable."""
    try:
        client = get_redis_client()
        return bool(client.ping())
    except Exception as exc:
        logger.warning(f"Redis health check failed: {exc}")
        return False