"""
Database Models
"""
from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base


class BaseRoute(Base):
    __tablename__ = "base_routes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    base_url = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    proxy_targets = Column(JSON, nullable=False)  # Array of provider configs
    rate_limits = Column(JSON, nullable=False)  # Rate limit config
    api_key_pool_id = Column(UUID(as_uuid=True), ForeignKey("api_key_pools.id"), nullable=False)
    routing_strategy = Column(String, nullable=False)  # ROUND_ROBIN, LEAST_USED, WEIGHTED
    fallback_policy = Column(JSON, nullable=False)
    enabled = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class APIKeyPool(Base):
    __tablename__ = "api_key_pools"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    pool_metadata = Column(JSON, default={})  # Renamed from 'metadata' to avoid SQLAlchemy conflict
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pool_id = Column(UUID(as_uuid=True), ForeignKey("api_key_pools.id"), nullable=False)
    provider_id = Column(String, nullable=False)
    secret_encrypted = Column(Text, nullable=False)  # Encrypted secret
    priority = Column(Integer, default=0)
    weight = Column(Integer, default=1)
    status = Column(String, default="healthy")  # healthy, unhealthy, disabled
    last_used = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class RequestLog(Base):
    __tablename__ = "requests_log"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    route_id = Column(UUID(as_uuid=True), ForeignKey("base_routes.id"), nullable=False)
    key_id = Column(UUID(as_uuid=True), ForeignKey("api_keys.id"), nullable=True)
    client_ip = Column(String, nullable=True)
    method = Column(String, nullable=False)
    path = Column(Text, nullable=False)
    response_status = Column(Integer, nullable=False)
    latency_ms = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)  # Hashed password
    name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class UserAPIKey(Base):
    __tablename__ = "user_api_keys"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    key_hash = Column(String, nullable=False, unique=True, index=True)  # Hashed API key
    name = Column(String, nullable=True)  # نام دلخواه برای کلید
    last_used = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserQuota(Base):
    __tablename__ = "user_quotas"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True, index=True)
    per_minute = Column(Integer, default=10, nullable=False)  # Limit per minute
    per_hour = Column(Integer, default=100, nullable=False)  # Limit per hour
    per_day = Column(Integer, default=1000, nullable=False)  # Limit per day
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

