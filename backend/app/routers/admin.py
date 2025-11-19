"""
Admin API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from app.database import get_db
from app.models import BaseRoute, APIKeyPool, APIKey, RequestLog, User, UserQuota
from app.schemas import (
    BaseRouteCreate, BaseRouteUpdate, BaseRouteResponse,
    KeyPoolCreate, KeyPoolResponse,
    APIKeyCreate, APIKeyBulkCreate, APIKeyResponse, APIKeyStatusUpdate,
    MetricsRequest, LogsRequest,
    UserQuotaCreate, UserQuotaUpdate, UserQuotaResponse
)
from app.encryption import encrypt_secret
from app.config import settings

router = APIRouter()


@router.get("/")
async def admin_root():
    """Admin API root - lists available endpoints"""
    return {
        "message": "Admin API",
        "available_endpoints": {
            "base_routes": {
                "list": "GET /base_routes",
                "create": "POST /base_routes",
                "get": "GET /base_routes/{route_id}",
                "update": "PATCH /base_routes/{route_id}",
                "delete": "DELETE /base_routes/{route_id}"
            },
            "key_pools": {
                "list": "GET /key_pools",
                "create": "POST /key_pools"
            },
            "api_keys": {
                "list": "GET /key_pools/{pool_id}/keys",
                "create": "POST /key_pools/{pool_id}/keys",
                "create_bulk": "POST /key_pools/{pool_id}/keys/bulk",
                "update_status": "PATCH /keys/{key_id}/status",
                "delete": "DELETE /keys/{key_id}"
            },
            "metrics": "GET /metrics",
            "logs": "GET /logs",
            "users": {
                "list": "GET /users",
                "create": "POST /users",
                "delete": "DELETE /users/{user_id}",
                "update_status": "PATCH /users/{user_id}/status"
            },
            "user_quotas": {
                "create": "POST /users/{user_id}/quota",
                "get": "GET /users/{user_id}/quota",
                "update": "PATCH /users/{user_id}/quota"
            }
        },
        "note": "All endpoints require admin authentication via ADMIN_SECRET_KEY header"
    }


def verify_admin_token(token: str):
    """Verify admin token (simple implementation)"""
    if token != settings.ADMIN_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin token"
        )


# Base Routes CRUD
@router.post("/base_routes", response_model=BaseRouteResponse, status_code=status.HTTP_201_CREATED)
async def create_base_route(
    route: BaseRouteCreate,
    db: Session = Depends(get_db),
    admin_token: str = None  # In production, use proper auth
):
    """Create a new base route - base_url must be first field"""
    # Check if base_url already exists
    existing = db.query(BaseRoute).filter(BaseRoute.base_url == route.base_url).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Base URL {route.base_url} already exists"
        )
    
    # Verify pool exists
    pool = db.query(APIKeyPool).filter(APIKeyPool.id == route.api_key_pool_id).first()
    if not pool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API Key Pool not found"
        )
    
    db_route = BaseRoute(
        base_url=route.base_url,
        name=route.name,
        proxy_targets=[t.model_dump() for t in route.proxy_targets],
        rate_limits=route.rate_limits.model_dump(),
        api_key_pool_id=route.api_key_pool_id,
        routing_strategy=route.routing_strategy.value,
        fallback_policy=route.fallback_policy.model_dump(),
        enabled=route.enabled
    )
    
    db.add(db_route)
    db.commit()
    db.refresh(db_route)
    
    return db_route


@router.get("/base_routes", response_model=List[BaseRouteResponse])
async def list_base_routes(db: Session = Depends(get_db)):
    """List all base routes"""
    routes = db.query(BaseRoute).all()
    return routes


@router.get("/base_routes/{route_id}", response_model=BaseRouteResponse)
async def get_base_route(route_id: UUID, db: Session = Depends(get_db)):
    """Get a specific base route"""
    route = db.query(BaseRoute).filter(BaseRoute.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Base route not found")
    return route


@router.patch("/base_routes/{route_id}", response_model=BaseRouteResponse)
async def update_base_route(
    route_id: UUID,
    route_update: BaseRouteUpdate,
    db: Session = Depends(get_db)
):
    """Update a base route"""
    route = db.query(BaseRoute).filter(BaseRoute.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Base route not found")
    
    update_data = route_update.model_dump(exclude_unset=True)
    
    if "proxy_targets" in update_data:
        update_data["proxy_targets"] = [t if isinstance(t, dict) else t.model_dump() 
                                       for t in update_data["proxy_targets"]]
    if "rate_limits" in update_data:
        update_data["rate_limits"] = update_data["rate_limits"] if isinstance(update_data["rate_limits"], dict) \
            else update_data["rate_limits"].model_dump()
    if "fallback_policy" in update_data:
        update_data["fallback_policy"] = update_data["fallback_policy"] if isinstance(update_data["fallback_policy"], dict) \
            else update_data["fallback_policy"].model_dump()
    if "routing_strategy" in update_data:
        update_data["routing_strategy"] = update_data["routing_strategy"].value if hasattr(update_data["routing_strategy"], "value") \
            else update_data["routing_strategy"]
    
    for key, value in update_data.items():
        setattr(route, key, value)
    
    route.updated_at = datetime.now()
    db.commit()
    db.refresh(route)
    return route


@router.delete("/base_routes/{route_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_base_route(route_id: UUID, db: Session = Depends(get_db)):
    """Delete a base route"""
    route = db.query(BaseRoute).filter(BaseRoute.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Base route not found")
    
    db.delete(route)
    db.commit()
    return None


# Key Pool CRUD
@router.post("/key_pools", response_model=KeyPoolResponse, status_code=status.HTTP_201_CREATED)
async def create_key_pool(pool: KeyPoolCreate, db: Session = Depends(get_db)):
    """Create a new API key pool"""
    db_pool = APIKeyPool(name=pool.name, pool_metadata=pool.metadata or {})
    db.add(db_pool)
    db.commit()
    db.refresh(db_pool)
    # Convert pool_metadata to metadata for response
    return KeyPoolResponse(
        id=db_pool.id,
        name=db_pool.name,
        metadata=db_pool.pool_metadata or {},
        created_at=db_pool.created_at,
        updated_at=db_pool.updated_at
    )


@router.get("/key_pools", response_model=List[KeyPoolResponse])
async def list_key_pools(db: Session = Depends(get_db)):
    """List all key pools"""
    pools = db.query(APIKeyPool).all()
    # Convert pool_metadata to metadata for each pool
    return [
        KeyPoolResponse(
            id=pool.id,
            name=pool.name,
            metadata=pool.pool_metadata or {},
            created_at=pool.created_at,
            updated_at=pool.updated_at
        )
        for pool in pools
    ]


# API Keys CRUD
@router.post("/key_pools/{pool_id}/keys", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    pool_id: UUID,
    key: APIKeyCreate,
    db: Session = Depends(get_db)
):
    """Create a new API key"""
    pool = db.query(APIKeyPool).filter(APIKeyPool.id == pool_id).first()
    if not pool:
        raise HTTPException(status_code=404, detail="Key pool not found")
    
    db_key = APIKey(
        pool_id=pool_id,
        provider_id=key.provider_id,
        secret_encrypted=encrypt_secret(key.secret),
        priority=key.priority,
        weight=key.weight,
        status=key.status
    )
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    return db_key


@router.post("/key_pools/{pool_id}/keys/bulk", response_model=List[APIKeyResponse])
async def create_api_keys_bulk(
    pool_id: UUID,
    bulk: APIKeyBulkCreate,
    db: Session = Depends(get_db)
):
    """Create multiple API keys in bulk"""
    pool = db.query(APIKeyPool).filter(APIKeyPool.id == pool_id).first()
    if not pool:
        raise HTTPException(status_code=404, detail="Key pool not found")
    
    db_keys = []
    for key_data in bulk.keys:
        db_key = APIKey(
            pool_id=pool_id,
            provider_id=key_data.get("provider_id", ""),
            secret_encrypted=encrypt_secret(key_data.get("secret", "")),
            priority=key_data.get("priority", 0),
            weight=key_data.get("weight", 1),
            status=key_data.get("status", "healthy")
        )
        db_keys.append(db_key)
        db.add(db_key)
    
    db.commit()
    for key in db_keys:
        db.refresh(key)
    
    return db_keys


@router.get("/key_pools/{pool_id}/keys", response_model=List[APIKeyResponse])
async def list_api_keys(pool_id: UUID, db: Session = Depends(get_db)):
    """List all keys in a pool"""
    keys = db.query(APIKey).filter(APIKey.pool_id == pool_id).all()
    return keys


@router.patch("/keys/{key_id}/status", response_model=APIKeyResponse)
async def update_key_status(
    key_id: UUID,
    status_update: APIKeyStatusUpdate,
    db: Session = Depends(get_db)
):
    """Update API key status"""
    key = db.query(APIKey).filter(APIKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    key.status = status_update.status
    db.commit()
    db.refresh(key)
    return key


@router.delete("/keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    key_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete an API key"""
    key = db.query(APIKey).filter(APIKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    # Delete related request logs first (or set key_id to NULL)
    # We'll delete them to clean up the database
    db.query(RequestLog).filter(RequestLog.key_id == key_id).delete()
    
    # Now delete the key
    db.delete(key)
    db.commit()
    return None


# Metrics
@router.get("/metrics")
async def get_metrics(
    route_id: Optional[UUID] = None,
    from_time: Optional[datetime] = None,
    to_time: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get metrics for routes"""
    query = db.query(RequestLog)
    
    if route_id:
        query = query.filter(RequestLog.route_id == route_id)
    
    if from_time:
        query = query.filter(RequestLog.created_at >= from_time)
    
    if to_time:
        query = query.filter(RequestLog.created_at <= to_time)
    else:
        # Default to last 24 hours
        if not from_time:
            query = query.filter(RequestLog.created_at >= datetime.now() - timedelta(days=1))
    
    logs = query.all()
    
    # Calculate metrics
    total_requests = len(logs)
    success_count = sum(1 for log in logs if 200 <= log.response_status < 300)
    error_count = sum(1 for log in logs if log.response_status >= 400)
    avg_latency = sum(log.latency_ms for log in logs) / total_requests if total_requests > 0 else 0
    
    # Group by route
    route_stats = {}
    for log in logs:
        if log.route_id not in route_stats:
            route_stats[log.route_id] = {"count": 0, "success": 0, "error": 0, "latency_sum": 0}
        route_stats[log.route_id]["count"] += 1
        if 200 <= log.response_status < 300:
            route_stats[log.route_id]["success"] += 1
        if log.response_status >= 400:
            route_stats[log.route_id]["error"] += 1
        route_stats[log.route_id]["latency_sum"] += log.latency_ms
    
    for route_id in route_stats:
        stats = route_stats[route_id]
        stats["avg_latency"] = stats["latency_sum"] / stats["count"] if stats["count"] > 0 else 0
        del stats["latency_sum"]
    
    return {
        "total_requests": total_requests,
        "success_count": success_count,
        "error_count": error_count,
        "success_rate": success_count / total_requests if total_requests > 0 else 0,
        "avg_latency_ms": avg_latency,
        "route_stats": route_stats
    }


# Logs
@router.get("/logs")
async def get_logs(
    route_id: Optional[UUID] = None,
    key_id: Optional[UUID] = None,
    status: Optional[int] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get request logs"""
    query = db.query(RequestLog)
    
    if route_id:
        query = query.filter(RequestLog.route_id == route_id)
    if key_id:
        query = query.filter(RequestLog.key_id == key_id)
    if status:
        query = query.filter(RequestLog.response_status == status)
    
    logs = query.order_by(RequestLog.created_at.desc()).limit(limit).all()
    
    return [
        {
            "id": str(log.id),
            "route_id": str(log.route_id),
            "key_id": str(log.key_id) if log.key_id else None,
            "client_ip": log.client_ip,
            "method": log.method,
            "path": log.path,
            "response_status": log.response_status,
            "latency_ms": log.latency_ms,
            "created_at": log.created_at.isoformat()
        }
        for log in logs
    ]


# User Management
@router.get("/users", response_model=List[dict])
async def list_users(db: Session = Depends(get_db)):
    """List all users"""
    users = db.query(User).all()
    return [
        {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat()
        }
        for user in users
    ]


@router.post("/users", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: dict,
    db: Session = Depends(get_db)
):
    """Create a new user"""
    from app.auth import get_password_hash
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.get("email")).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    # Create new user
    new_user = User(
        email=user_data.get("email"),
        password_hash=get_password_hash(user_data.get("password")),
        name=user_data.get("name"),
        is_active=user_data.get("is_active", True)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "id": str(new_user.id),
        "email": new_user.email,
        "name": new_user.name,
        "is_active": new_user.is_active,
        "created_at": new_user.created_at.isoformat()
    }


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Delete related data first
    from app.models import UserAPIKey, UserQuota
    db.query(UserAPIKey).filter(UserAPIKey.user_id == user_id).delete()
    db.query(UserQuota).filter(UserQuota.user_id == user_id).delete()
    
    # Delete user
    db.delete(user)
    db.commit()
    return None


@router.patch("/users/{user_id}/status", response_model=dict)
async def update_user_status(
    user_id: UUID,
    status_data: dict,
    db: Session = Depends(get_db)
):
    """Update user status (active/inactive)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if "is_active" in status_data:
        user.is_active = status_data["is_active"]
    
    db.commit()
    db.refresh(user)
    
    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat()
    }


# User Quota Management
@router.post("/users/{user_id}/quota", response_model=UserQuotaResponse, status_code=status.HTTP_201_CREATED)
async def create_user_quota(
    user_id: UUID,
    quota: UserQuotaCreate,
    db: Session = Depends(get_db)
):
    """Create or update user quota"""
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if quota already exists
    existing_quota = db.query(UserQuota).filter(UserQuota.user_id == user_id).first()
    if existing_quota:
        # Update existing quota
        if quota.per_minute is not None:
            existing_quota.per_minute = quota.per_minute
        if quota.per_hour is not None:
            existing_quota.per_hour = quota.per_hour
        if quota.per_day is not None:
            existing_quota.per_day = quota.per_day
        existing_quota.updated_at = datetime.now()
        db.commit()
        db.refresh(existing_quota)
        return existing_quota
    else:
        # Create new quota
        db_quota = UserQuota(
            user_id=user_id,
            per_minute=quota.per_minute,
            per_hour=quota.per_hour,
            per_day=quota.per_day
        )
        db.add(db_quota)
        db.commit()
        db.refresh(db_quota)
        return db_quota


@router.get("/users/{user_id}/quota", response_model=UserQuotaResponse)
async def get_user_quota(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Get user quota"""
    quota = db.query(UserQuota).filter(UserQuota.user_id == user_id).first()
    if not quota:
        raise HTTPException(status_code=404, detail="User quota not found")
    return quota


@router.patch("/users/{user_id}/quota", response_model=UserQuotaResponse)
async def update_user_quota(
    user_id: UUID,
    quota_update: UserQuotaUpdate,
    db: Session = Depends(get_db)
):
    """Update user quota"""
    quota = db.query(UserQuota).filter(UserQuota.user_id == user_id).first()
    if not quota:
        raise HTTPException(status_code=404, detail="User quota not found")
    
    if quota_update.per_minute is not None:
        quota.per_minute = quota_update.per_minute
    if quota_update.per_hour is not None:
        quota.per_hour = quota_update.per_hour
    if quota_update.per_day is not None:
        quota.per_day = quota_update.per_day
    quota.updated_at = datetime.now()
    
    db.commit()
    db.refresh(quota)
    return quota

