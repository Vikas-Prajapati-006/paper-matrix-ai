from app.core.config import settings
from app.core.errors import QuotaExceededException
from app.core.logger import logger
from app.db.redis_client import get_redis_client


class CreditLimiter:
    def __init__(self):
        self.redis = get_redis_client()
        self.max_credits = settings.FREE_CREDITS_PER_DEVICE
        self.window = settings.CREDIT_WINDOW_SECONDS

    def _get_key(self, fingerprint: str) -> str:
        return f"quota:{fingerprint}"

    def check_and_consume_credit(self, fingerprint: str) -> dict:
        """Atomically checks and consumes 1 credit if available.
        
        Returns remaining credits and TTL.
        """
        key = self._get_key(fingerprint)
        try:
            pipe = self.redis.pipeline()
            pipe.get(key)
            pipe.ttl(key)
            results = pipe.execute()

            raw_used = results[0]
            ttl = results[1]

            used_credits = int(raw_used) if raw_used is not None else 0

            if used_credits >= self.max_credits:
                raise QuotaExceededException(
                    f"Daily free limit of {self.max_credits} papers reached. Resets in {ttl} seconds."
                )

            # Atomic increment and TTL establishment
            pipe = self.redis.pipeline()
            pipe.incr(key)
            if used_credits == 0 or ttl == -1:
                pipe.expire(key, self.window)
            pipe.execute()

            remaining = self.max_credits - (used_credits + 1)
            return {"remaining": remaining, "ttl": max(ttl, 0)}

        except QuotaExceededException:
            raise
        except Exception as exc:
            logger.warning(f"Quota limiter bypass due to Redis error: {exc}")
            # Graceful fallback: agar Redis temporarily down ho toh request block na ho
            return {"remaining": 1, "ttl": 0}

    def get_remaining_credits(self, fingerprint: str) -> dict:
        """Read-only check for quota status without decrementing."""
        key = self._get_key(fingerprint)
        try:
            raw_used = self.redis.get(key)
            ttl = self.redis.ttl(key)
            used = int(raw_used) if raw_used is not None else 0
            remaining = max(0, self.max_credits - used)
            return {"remaining": remaining, "ttl": max(ttl, 0)}
        except Exception as exc:
            logger.warning(f"Failed to fetch credit balance: {exc}")
            return {"remaining": self.max_credits, "ttl": 0}


limiter = CreditLimiter()