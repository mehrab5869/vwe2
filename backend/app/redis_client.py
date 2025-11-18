"""
Redis Client and Utilities
"""
import redis
from app.config import settings
from typing import Optional
import json

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


# Lua scripts for atomic operations
RATE_LIMIT_SCRIPT = """
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local current = redis.call('INCR', key)
if current == 1 then
    redis.call('EXPIRE', key, window)
end
if current > limit then
    return {0, current, window}
end
return {1, current, window}
"""

rate_limit_script = redis_client.register_script(RATE_LIMIT_SCRIPT)


def check_rate_limit(key: str, limit: int, window_seconds: int) -> tuple[bool, int, int]:
    """
    Check rate limit atomically
    Returns: (allowed, current_count, retry_after_seconds)
    """
    result = rate_limit_script(keys=[key], args=[limit, window_seconds])
    allowed = result[0] == 1
    current = result[1]
    retry_after = window_seconds if not allowed else 0
    return allowed, current, retry_after


def increment_counter(key: str, ttl: Optional[int] = None):
    """Increment a counter with optional TTL"""
    pipe = redis_client.pipeline()
    pipe.incr(key)
    if ttl:
        pipe.expire(key, ttl)
    pipe.execute()


def get_counter(key: str) -> int:
    """Get counter value"""
    return int(redis_client.get(key) or 0)


def set_key_health(pool_id: str, key_id: str, status: str, ttl: Optional[int] = None):
    """Set key health status with optional TTL"""
    key = f"pool:{pool_id}:key:{key_id}:health"
    redis_client.set(key, status)
    if ttl:
        redis_client.expire(key, ttl)


def get_key_health(pool_id: str, key_id: str) -> Optional[str]:
    """Get key health status"""
    key = f"pool:{pool_id}:key:{key_id}:health"
    return redis_client.get(key)


def clear_key_health(pool_id: str, key_id: str):
    """Clear key health status from Redis"""
    key = f"pool:{pool_id}:key:{key_id}:health"
    redis_client.delete(key)


def get_round_robin_pointer(pool_id: str) -> int:
    """Get current round-robin pointer"""
    key = f"pool:{pool_id}:rr_pointer"
    return int(redis_client.get(key) or 0)


def set_round_robin_pointer(pool_id: str, value: int):
    """Set round-robin pointer"""
    key = f"pool:{pool_id}:rr_pointer"
    redis_client.set(key, value)

