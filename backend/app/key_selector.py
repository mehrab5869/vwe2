"""
Key Selection Strategies
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import APIKey
from app.redis_client import (
    get_key_health, get_round_robin_pointer, set_round_robin_pointer,
    get_counter
)
from app.config import settings
import redis
from datetime import datetime
import random

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


def select_key_round_robin(
    db: Session,
    pool_id: str,
    provider_id: str,
    healthy_only: bool = True
) -> Optional[APIKey]:
    """Select key using round-robin strategy"""
    # Convert pool_id to UUID if it's a string
    from uuid import UUID
    if isinstance(pool_id, str):
        try:
            pool_id = UUID(pool_id)
        except:
            pass
    
    query = db.query(APIKey).filter(
        APIKey.pool_id == pool_id,
        APIKey.provider_id == provider_id,
        APIKey.status.in_(["healthy", "unhealthy"])
    )
    
    all_keys = query.all()
    print(f"[KEY_SELECTOR] Found {len(all_keys)} keys for pool={pool_id}, provider={provider_id}")
    
    if healthy_only:
        keys = []
        for k in all_keys:
            # Check Redis health status
            redis_health = get_key_health(str(pool_id), str(k.id))
            print(f"[KEY_SELECTOR] Key {k.id}: db_status={k.status}, redis_health={redis_health}")
            
            # If key is disabled in DB, skip it
            if k.status == "disabled":
                continue
            
            # If key is healthy in DB, include it (Redis health is temporary)
            # Only exclude if Redis explicitly marks it unhealthy AND DB status is also unhealthy
            if k.status == "healthy":
                keys.append(k)
            elif k.status == "unhealthy" and redis_health != "unhealthy":
                # DB says unhealthy but Redis doesn't - might be recovered, include it
                keys.append(k)
            # If both DB and Redis say unhealthy, exclude it
    else:
        keys = all_keys
    
    print(f"[KEY_SELECTOR] Filtered to {len(keys)} healthy keys")
    
    if not keys:
        return None
    
    pointer = get_round_robin_pointer(str(pool_id))
    selected = keys[pointer % len(keys)]
    set_round_robin_pointer(str(pool_id), (pointer + 1) % len(keys))
    
    print(f"[KEY_SELECTOR] Selected key: {selected.id}")
    return selected


def select_key_least_used(
    db: Session,
    pool_id: str,
    provider_id: str,
    healthy_only: bool = True
) -> Optional[APIKey]:
    """Select key with least usage today"""
    query = db.query(APIKey).filter(
        APIKey.pool_id == pool_id,
        APIKey.provider_id == provider_id,
        APIKey.status.in_(["healthy", "unhealthy"])
    )
    
    keys = query.all()
    if not keys:
        return None
    
    today = datetime.now().strftime("%Y%m%d")
    usage_map = {}
    
    for key in keys:
        # Filter by health: if key is disabled in DB, skip it
        if key.status == "disabled":
            continue
        
        # If healthy_only, check both DB and Redis status
        if healthy_only:
            redis_health = get_key_health(str(pool_id), str(key.id))
            # Only exclude if both DB and Redis say unhealthy
            if key.status == "unhealthy" and redis_health == "unhealthy":
                continue
        
        usage_key = f"pool:{pool_id}:key:{key.id}:usage:day:{today}"
        usage = get_counter(usage_key)
        usage_map[key] = usage
    
    if not usage_map:
        return None
    
    # Select key with minimum usage
    selected = min(usage_map.items(), key=lambda x: x[1])[0]
    return selected


def select_key_weighted(
    db: Session,
    pool_id: str,
    provider_id: str,
    healthy_only: bool = True
) -> Optional[APIKey]:
    """Select key using weighted random selection"""
    query = db.query(APIKey).filter(
        APIKey.pool_id == pool_id,
        APIKey.provider_id == provider_id,
        APIKey.status.in_(["healthy", "unhealthy"])
    )
    
    keys = query.all()
    if not keys:
        return None
    
    # Filter healthy keys
    valid_keys = []
    for key in keys:
        # If key is disabled in DB, skip it
        if key.status == "disabled":
            continue
        
        # If healthy_only, check both DB and Redis status
        if healthy_only:
            redis_health = get_key_health(str(pool_id), str(key.id))
            # Only exclude if both DB and Redis say unhealthy
            if key.status == "unhealthy" and redis_health == "unhealthy":
                continue
        
        valid_keys.append(key)
    
    if not valid_keys:
        return None
    
    # Weighted random selection
    weights = [k.weight for k in valid_keys]
    total_weight = sum(weights)
    
    if total_weight == 0:
        return random.choice(valid_keys)
    
    r = random.uniform(0, total_weight)
    cumulative = 0
    
    for i, weight in enumerate(weights):
        cumulative += weight
        if r <= cumulative:
            return valid_keys[i]
    
    return valid_keys[-1]


def select_key(
    db: Session,
    pool_id: str,
    provider_id: str,
    strategy: str,
    healthy_only: bool = True
) -> Optional[APIKey]:
    """Select key based on strategy"""
    if strategy == "ROUND_ROBIN":
        return select_key_round_robin(db, pool_id, provider_id, healthy_only)
    elif strategy == "LEAST_USED":
        return select_key_least_used(db, pool_id, provider_id, healthy_only)
    elif strategy == "WEIGHTED":
        return select_key_weighted(db, pool_id, provider_id, healthy_only)
    else:
        # Default to round-robin
        return select_key_round_robin(db, pool_id, provider_id, healthy_only)

