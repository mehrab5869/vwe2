import sys
import os
# Add backend and backend/app to path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
backend_app_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'app')
if backend_app_path not in sys.path:
    sys.path.insert(0, backend_app_path)

# Import config to get REDIS_URL
from app.config import REDIS_URL

# Try to connect to Redis with fallback
import redis
from typing import Optional
import json

try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    # Test connection
    redis_client.ping()
    print(f"Connected to Redis: {REDIS_URL}")
    redis_available = True
except Exception as e:
    print(f"Warning: Could not connect to Redis: {e}")
    print("Continuing without Redis...")
    redis_client = None
    redis_available = False

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

rate_limit_script = redis_client.register_script(RATE_LIMIT_SCRIPT) if redis_available else None


def check_rate_limit(key: str, limit: int, window_seconds: int) -> tuple[bool, int, int]:
    """
    Check rate limit atomically
    Returns: (allowed, current_count, retry_after_seconds)
    """
    if not redis_available or not rate_limit_script:
        # If Redis is not available, always allow requests
        return True, 0, 0
    
    try:
        result = rate_limit_script(keys=[key], args=[limit, window_seconds])
        allowed = result[0] == 1
        current = result[1]
        retry_after = window_seconds if not allowed else 0
        return allowed, current, retry_after
    except Exception:
        # Fallback to allowing requests if Redis fails
        return True, 0, 0


def increment_counter(key: str, ttl: Optional[int] = None):
    """Increment a counter with optional TTL"""
    if not redis_available:
        return
    
    try:
        pipe = redis_client.pipeline()
        pipe.incr(key)
        if ttl:
            pipe.expire(key, ttl)
        pipe.execute()
    except Exception:
        pass


def get_counter(key: str) -> int:
    """Get counter value"""
    if not redis_available:
        return 0
    
    try:
        return int(redis_client.get(key) or 0)
    except Exception:
        return 0


def set_key_health(pool_id: str, key_id: str, status: str, ttl: Optional[int] = None):
    """Set key health status with optional TTL"""
    if not redis_available:
        return
    
    try:
        key = f"pool:{pool_id}:key:{key_id}:health"
        redis_client.set(key, status)
        if ttl:
            redis_client.expire(key, ttl)
    except Exception:
        pass


def get_key_health(pool_id: str, key_id: str) -> Optional[str]:
    """Get key health status"""
    if not redis_available:
        return None
    
    try:
        key = f"pool:{pool_id}:key:{key_id}:health"
        return redis_client.get(key)
    except Exception:
        return None


def clear_key_health(pool_id: str, key_id: str):
    """Clear key health status from Redis"""
    if not redis_available:
        return
    
    try:
        key = f"pool:{pool_id}:key:{key_id}:health"
        redis_client.delete(key)
    except Exception:
        pass


def get_round_robin_pointer(pool_id: str) -> int:
    """Get current round-robin pointer"""
    if not redis_available:
        return 0
    
    try:
        key = f"pool:{pool_id}:rr_pointer"
        return int(redis_client.get(key) or 0)
    except Exception:
        return 0


def set_round_robin_pointer(pool_id: str, value: int):
    """Set round-robin pointer"""
    if not redis_available:
        return
    
    try:
        key = f"pool:{pool_id}:rr_pointer"
        redis_client.set(key, value)
    except Exception:
        pass