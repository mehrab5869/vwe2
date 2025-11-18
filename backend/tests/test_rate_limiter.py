"""
Unit tests for rate limiting logic
"""
import pytest
from datetime import datetime
from app.rate_limiter import check_route_rate_limits
from app.schemas import RateLimits
from app.redis_client import redis_client


@pytest.fixture
def cleanup_redis():
    """Cleanup Redis before and after tests"""
    yield
    # Cleanup test keys
    keys = redis_client.keys("base:/test*")
    if keys:
        redis_client.delete(*keys)


def test_rate_limit_per_minute(cleanup_redis):
    """Test per-minute rate limiting"""
    rate_limits = RateLimits(
        per_minute=5,
        per_day=1000
    )
    
    base_url = "/test"
    
    # First 5 requests should pass
    for i in range(5):
        allowed, retry_after = check_route_rate_limits(base_url, rate_limits, None)
        assert allowed, f"Request {i+1} should be allowed"
    
    # 6th request should be blocked
    allowed, retry_after = check_route_rate_limits(base_url, rate_limits, None)
    assert not allowed, "6th request should be blocked"
    assert retry_after > 0, "Should return retry_after"


def test_rate_limit_per_ip(cleanup_redis):
    """Test per-IP rate limiting"""
    rate_limits = RateLimits(
        per_minute=100,
        per_day=1000,
        per_ip={"per_minute": 3, "per_day": 100}
    )
    
    base_url = "/test"
    client_ip = "192.168.1.1"
    
    # First 3 requests from this IP should pass
    for i in range(3):
        allowed, retry_after = check_route_rate_limits(base_url, rate_limits, client_ip)
        assert allowed, f"Request {i+1} should be allowed"
    
    # 4th request should be blocked
    allowed, retry_after = check_route_rate_limits(base_url, rate_limits, client_ip)
    assert not allowed, "4th request should be blocked"


def test_different_ips_independent(cleanup_redis):
    """Test that different IPs have independent limits"""
    rate_limits = RateLimits(
        per_minute=100,
        per_day=1000,
        per_ip={"per_minute": 2}
    )
    
    base_url = "/test"
    
    # IP1: 2 requests
    for i in range(2):
        allowed, _ = check_route_rate_limits(base_url, rate_limits, "192.168.1.1")
        assert allowed
    
    # IP2: Should still be able to make requests
    allowed, _ = check_route_rate_limits(base_url, rate_limits, "192.168.1.2")
    assert allowed, "Different IP should have independent limit"

