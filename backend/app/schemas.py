"""
Pydantic Schemas for Request/Response Validation
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


class RoutingStrategy(str, Enum):
    ROUND_ROBIN = "ROUND_ROBIN"
    LEAST_USED = "LEAST_USED"
    WEIGHTED = "WEIGHTED"


class FallbackOnExhaust(str, Enum):
    TRY_OTHER_PROVIDER = "TRY_OTHER_PROVIDER"
    RETURN_429 = "RETURN_429"
    QUEUE = "QUEUE"
    FAILOVER_TO_STATIC_KEY = "FAILOVER_TO_STATIC_KEY"


class ProxyTarget(BaseModel):
    provider_id: str
    endpoint_template: str
    allowed_models: List[str]
    weight: Optional[int] = 1


class RateLimits(BaseModel):
    per_minute: int
    per_hour: Optional[int] = None
    per_day: int
    per_ip: Optional[Dict[str, int]] = None


class FallbackPolicy(BaseModel):
    on_exhaust: FallbackOnExhaust
    retry_attempts: int
    retry_backoff_ms: int


# Base Route Schemas
class BaseRouteCreate(BaseModel):
    base_url: str = Field(..., description="Base URL path (e.g., /v1) - FIRST FIELD")
    name: str
    proxy_targets: List[ProxyTarget]
    rate_limits: RateLimits
    api_key_pool_id: UUID
    routing_strategy: RoutingStrategy
    fallback_policy: FallbackPolicy
    enabled: bool = True

    @field_validator('base_url')
    def validate_base_url(cls, v):
        if not v.startswith('/'):
            raise ValueError('base_url must start with /')
        return v


class BaseRouteUpdate(BaseModel):
    name: Optional[str] = None
    proxy_targets: Optional[List[ProxyTarget]] = None
    rate_limits: Optional[RateLimits] = None
    api_key_pool_id: Optional[UUID] = None
    routing_strategy: Optional[RoutingStrategy] = None
    fallback_policy: Optional[FallbackPolicy] = None
    enabled: Optional[bool] = None


class BaseRouteResponse(BaseModel):
    id: UUID
    base_url: str
    name: str
    proxy_targets: List[ProxyTarget]
    rate_limits: RateLimits
    api_key_pool_id: UUID
    routing_strategy: RoutingStrategy
    fallback_policy: FallbackPolicy
    enabled: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Key Pool Schemas
class KeyPoolCreate(BaseModel):
    name: str
    metadata: Optional[Dict[str, Any]] = {}


class KeyPoolResponse(BaseModel):
    id: UUID
    name: str
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# API Key Schemas
class APIKeyCreate(BaseModel):
    pool_id: UUID
    provider_id: str
    secret: str  # Will be encrypted before storage
    priority: int = 0
    weight: int = 1
    status: str = "healthy"


class APIKeyBulkCreate(BaseModel):
    pool_id: UUID
    keys: List[Dict[str, str]]  # [{"provider_id": "...", "secret": "...", "priority": 0, "weight": 1}]


class APIKeyResponse(BaseModel):
    id: UUID
    pool_id: UUID
    provider_id: str
    priority: int
    weight: int
    status: str
    last_used: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class APIKeyStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(healthy|unhealthy|disabled)$")


# Metrics Schemas
class MetricsRequest(BaseModel):
    route_id: Optional[UUID] = None
    from_time: Optional[datetime] = None
    to_time: Optional[datetime] = None


class LogsRequest(BaseModel):
    route_id: Optional[UUID] = None
    key_id: Optional[UUID] = None
    status: Optional[int] = None
    limit: int = 100


# User Quota Schemas
class UserQuotaCreate(BaseModel):
    user_id: UUID
    per_minute: int = 10
    per_hour: int = 100
    per_day: int = 1000


class UserQuotaUpdate(BaseModel):
    per_minute: Optional[int] = None
    per_hour: Optional[int] = None
    per_day: Optional[int] = None


class UserQuotaResponse(BaseModel):
    id: UUID
    user_id: UUID
    per_minute: int
    per_hour: int
    per_day: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

