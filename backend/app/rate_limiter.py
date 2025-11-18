"""
Rate Limiting Logic
"""
from typing import Optional, Tuple
from datetime import datetime
from app.redis_client import check_rate_limit, increment_counter
from app.schemas import RateLimits


def check_route_rate_limits(
    base_url: str,
    rate_limits: RateLimits,
    client_ip: Optional[str] = None,
    key_id: Optional[str] = None
) -> Tuple[bool, Optional[int]]:
    """
    Check all rate limits for a route
    If key_id is provided, checks per-key limits first, then falls back to global limits
    Returns: (allowed, retry_after_seconds)
    """
    now = datetime.now()
    
    # Per-key rate limits (if key_id provided)
    if key_id:
        # Per-key per-minute limit (uses route's per_minute limit per key)
        key_min = f"base:{base_url}:key:{key_id}:min:{now.strftime('%Y%m%d%H%M')}"
        allowed, current, retry_after = check_rate_limit(key_min, rate_limits.per_minute, 60)
        if not allowed:
            return False, retry_after
        
        # Per-key per-hour limit
        if rate_limits.per_hour:
            key_hour = f"base:{base_url}:key:{key_id}:hour:{now.strftime('%Y%m%d%H')}"
            allowed, current, retry_after = check_rate_limit(key_hour, rate_limits.per_hour, 3600)
            if not allowed:
                return False, retry_after
        
        # Per-key per-day limit
        key_day = f"base:{base_url}:key:{key_id}:day:{now.strftime('%Y%m%d')}"
        allowed, current, retry_after = check_rate_limit(key_day, rate_limits.per_day, 86400)
        if not allowed:
            return False, retry_after
    
    # Global per-minute limit (fallback if no key_id or after per-key check)
    key_min = f"base:{base_url}:global:min:{now.strftime('%Y%m%d%H%M')}"
    allowed, current, retry_after = check_rate_limit(key_min, rate_limits.per_minute, 60)
    if not allowed:
        return False, retry_after
    
    # Global per-hour limit
    if rate_limits.per_hour:
        key_hour = f"base:{base_url}:global:hour:{now.strftime('%Y%m%d%H')}"
        allowed, current, retry_after = check_rate_limit(key_hour, rate_limits.per_hour, 3600)
        if not allowed:
            return False, retry_after
    
    # Global per-day limit
    key_day = f"base:{base_url}:global:day:{now.strftime('%Y%m%d')}"
    allowed, current, retry_after = check_rate_limit(key_day, rate_limits.per_day, 86400)
    if not allowed:
        return False, retry_after
    
    # Per-IP limits
    if client_ip and rate_limits.per_ip:
        if rate_limits.per_ip.get("per_minute"):
            ip_key_min = f"base:{base_url}:ip:{client_ip}:min:{now.strftime('%Y%m%d%H%M')}"
            allowed, current, retry_after = check_rate_limit(
                ip_key_min, rate_limits.per_ip["per_minute"], 60
            )
            if not allowed:
                return False, retry_after
        
        if rate_limits.per_ip.get("per_day"):
            ip_key_day = f"base:{base_url}:ip:{client_ip}:day:{now.strftime('%Y%m%d')}"
            allowed, current, retry_after = check_rate_limit(
                ip_key_day, rate_limits.per_ip["per_day"], 86400
            )
            if not allowed:
                return False, retry_after
    
    return True, None


def increment_usage_counters(
    base_url: str,
    pool_id: str,
    key_id: str,
    client_ip: Optional[str] = None
):
    """Increment all relevant usage counters"""
    now = datetime.now()
    
    # Per-key counters (for per-key rate limiting)
    increment_counter(f"base:{base_url}:key:{key_id}:min:{now.strftime('%Y%m%d%H%M')}", 60)
    increment_counter(f"base:{base_url}:key:{key_id}:hour:{now.strftime('%Y%m%d%H')}", 3600)
    increment_counter(f"base:{base_url}:key:{key_id}:day:{now.strftime('%Y%m%d')}", 86400)
    
    # Global counters
    increment_counter(f"base:{base_url}:global:min:{now.strftime('%Y%m%d%H%M')}", 60)
    increment_counter(f"base:{base_url}:global:hour:{now.strftime('%Y%m%d%H')}", 3600)
    increment_counter(f"base:{base_url}:global:day:{now.strftime('%Y%m%d')}", 86400)
    
    # Per-IP counters
    if client_ip:
        increment_counter(f"base:{base_url}:ip:{client_ip}:min:{now.strftime('%Y%m%d%H%M')}", 60)
        increment_counter(f"base:{base_url}:ip:{client_ip}:day:{now.strftime('%Y%m%d')}", 86400)
    
    # Per-key usage (for statistics)
    increment_counter(f"pool:{pool_id}:key:{key_id}:usage:day:{now.strftime('%Y%m%d')}", 86400)


def check_user_quota(
    user_id,
    user_quota,
    client_ip: Optional[str] = None
) -> Tuple[bool, Optional[int]]:
    """
    Check user quota limits
    Returns: (allowed, retry_after_seconds)
    """
    from app.models import UserQuota
    now = datetime.now()
    
    # Per-minute limit
    key_min = f"user:{user_id}:min:{now.strftime('%Y%m%d%H%M')}"
    allowed, current, retry_after = check_rate_limit(key_min, user_quota.per_minute, 60)
    if not allowed:
        return False, retry_after
    
    # Per-hour limit
    key_hour = f"user:{user_id}:hour:{now.strftime('%Y%m%d%H')}"
    allowed, current, retry_after = check_rate_limit(key_hour, user_quota.per_hour, 3600)
    if not allowed:
        return False, retry_after
    
    # Per-day limit
    key_day = f"user:{user_id}:day:{now.strftime('%Y%m%d')}"
    allowed, current, retry_after = check_rate_limit(key_day, user_quota.per_day, 86400)
    if not allowed:
        return False, retry_after
    
    return True, None


def increment_user_usage(
    user_id,
    client_ip: Optional[str] = None
):
    """Increment user usage counters"""
    now = datetime.now()
    
    # User counters
    increment_counter(f"user:{user_id}:min:{now.strftime('%Y%m%d%H%M')}", 60)
    increment_counter(f"user:{user_id}:hour:{now.strftime('%Y%m%d%H')}", 3600)
    increment_counter(f"user:{user_id}:day:{now.strftime('%Y%m%d')}", 86400)

