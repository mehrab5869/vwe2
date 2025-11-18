"""
Public Gateway - Handles all proxied requests
"""
from fastapi import APIRouter, Request, Response, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
import httpx
import time
import uuid as uuid_lib
import asyncio
from datetime import datetime
from urllib.parse import urlparse

from app.database import get_db
from app.models import BaseRoute, APIKey, RequestLog
from app.rate_limiter import check_route_rate_limits, increment_usage_counters, check_user_quota, increment_user_usage
from app.key_selector import select_key
from app.encryption import decrypt_secret
from app.redis_client import set_key_health, get_key_health
from app.schemas import ProxyTarget, FallbackOnExhaust

router = APIRouter()


def find_matching_route(path: str, db: Session) -> Optional[BaseRoute]:
    """Find route matching the path (exact match first, then prefix)"""
    # Try exact match first
    routes = db.query(BaseRoute).filter(
        BaseRoute.enabled == True
    ).all()
    
    # Sort by base_url length (longer first) for prefix matching
    routes.sort(key=lambda r: len(r.base_url), reverse=True)
    
    for route in routes:
        if path == route.base_url or path.startswith(route.base_url + "/"):
            return route
    
    return None


def validate_model_allowed(model: str, proxy_targets: list) -> tuple[bool, Optional[dict]]:
    """Check if model is allowed in any proxy target"""
    for target in proxy_targets:
        target_obj = ProxyTarget(**target) if isinstance(target, dict) else target
        if model in target_obj.allowed_models:
            return True, target_obj
    return False, None


async def forward_request(
    method: str,
    url: str,
    headers: dict,
    body: bytes,
    timeout: float = 30.0
) -> tuple[int, dict, bytes]:
    """Forward request to provider"""
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.request(
            method=method,
            url=url,
            headers=headers,
            content=body
        )
        return response.status_code, dict(response.headers), await response.aread()


def build_provider_url(template: str, model: str, path: str, base_url: str) -> str:
    """Build provider URL from template"""
    # Replace {model} placeholder
    url = template.replace("{model}", model)
    
    # If template already contains the full endpoint path, use it as-is
    # Check if template looks like a complete endpoint (contains /chat/completions or /completions)
    if "/chat/completions" in url or "/completions" in url:
        # Template is already complete, don't append path
        return url
    
    # Extract the path after base_url
    # path comes as full path like "/v1/chat/completions"
    # base_url is "/v1"
    # we need to get "chat/completions"
    if path.startswith(base_url):
        remaining_path = path[len(base_url):]
        if remaining_path.startswith("/"):
            remaining_path = remaining_path[1:]
        
        # Append remaining path if needed
        if remaining_path and "{path}" in url:
            url = url.replace("{path}", remaining_path)
        elif remaining_path:
            # Only append if template doesn't already have a path
            if not url.rstrip("/").endswith(("/chat/completions", "/completions")):
                url = url.rstrip("/") + "/" + remaining_path
    elif not path.startswith("/"):
        # If path doesn't start with /, it might be relative
        if not url.rstrip("/").endswith(("/chat/completions", "/completions")):
            url = url.rstrip("/") + "/" + path
    
    return url


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def gateway_proxy(
    path: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Main gateway endpoint - proxies all requests matching base_url routes
    Users can authenticate with their API key in Authorization header
    """
    start_time = time.time()
    request_id = str(uuid_lib.uuid4())
    client_ip = request.client.host if request.client else None
    
    # Check for user API key in Authorization header (optional - for tracking)
    user_api_key = None
    user = None
    user_quota = None
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        api_key = auth_header.replace("Bearer ", "").strip()
        if api_key.startswith("sk_"):
            # This is a user API key - verify it
            from app.auth import get_user_from_api_key
            from app.models import UserQuota
            user = get_user_from_api_key(api_key, db)
            if user:
                user_api_key = api_key
                # Get user quota
                user_quota = db.query(UserQuota).filter(UserQuota.user_id == user.id).first()
                print(f"[GATEWAY] Request from user: {user.email}, quota: {user_quota.per_day if user_quota else 'unlimited'}")
    
    # Find matching route
    route = find_matching_route(f"/{path}" if not path.startswith("/") else path, db)
    
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    
    # Extract model from request (check body or query params)
    model = None
    body_bytes = await request.body()
    
    try:
        import json
        if body_bytes:
            body_json = json.loads(body_bytes)
            model = body_json.get("model") or body_json.get("model_id")
    except:
        pass
    
    if not model:
        # Try query params
        model = request.query_params.get("model")
    
    if not model:
        raise HTTPException(
            status_code=400,
            detail="Model parameter is required"
        )
    
    # Validate model is allowed
    is_allowed, target = validate_model_allowed(model, route.proxy_targets)
    if not is_allowed or not target:
        raise HTTPException(
            status_code=400,
            detail=f"Model {model} is not supported for this route"
        )
    
    # Select API key based on strategy (we'll check rate limits per key)
    selected_key = None
    selected_target = target
    retry_count = 0
    max_retries = route.fallback_policy.get("retry_attempts", 2)
    backoff_ms = route.fallback_policy.get("retry_backoff_ms", 300)
    fallback_on_exhaust = route.fallback_policy.get("on_exhaust", "RETURN_429")
    
    # Try providers in order (weighted selection if multiple)
    proxy_targets = [ProxyTarget(**t) if isinstance(t, dict) else t for t in route.proxy_targets]
    
    # Sort by weight (descending) for fallback
    sorted_targets = sorted(proxy_targets, key=lambda t: t.weight or 1, reverse=True)
    
    last_error = None
    response_status = None
    response_headers = {}
    response_body = b""
    
    # Log for debugging - use print for now
    print(f"[GATEWAY] Processing: route={route.base_url}, model={model}, pool_id={route.api_key_pool_id}, provider={selected_target.provider_id}")
    
    # Try keys until we find one that passes rate limits
    from app.schemas import RateLimits
    rate_limits = RateLimits(**route.rate_limits)
    tried_keys = set()  # Track which keys we've tried for rate limits
    max_key_tries = 50  # Maximum attempts to find a key that passes rate limits
    
    for attempt in range(max_retries + 1):
        key_try_count = 0
        
        # Try to find a key that passes rate limits
        while key_try_count < max_key_tries:
            # Select key for current target
            print(f"[GATEWAY] Attempt {attempt + 1}, Key try {key_try_count + 1}: Selecting key for provider={selected_target.provider_id}")
            selected_key = select_key(
                db=db,
                pool_id=str(route.api_key_pool_id),
                provider_id=selected_target.provider_id,
                strategy=route.routing_strategy,
                healthy_only=True
            )
            
            if not selected_key:
                break  # No more keys available
            
            # Skip if we've already tried this key
            if str(selected_key.id) in tried_keys:
                key_try_count += 1
                continue
            
            # Check rate limits for this specific key
            print(f"[GATEWAY] Checking rate limits for key={selected_key.id}")
            allowed, retry_after = check_route_rate_limits(
                route.base_url,
                rate_limits,
                client_ip,
                str(selected_key.id)
            )
            
            if not allowed:
                print(f"[GATEWAY] Key {selected_key.id} rate limit exceeded (per_minute={rate_limits.per_minute}), trying next key")
                tried_keys.add(str(selected_key.id))
                key_try_count += 1
                continue  # Try next key
            
            # Found a key that passes rate limits!
            print(f"[GATEWAY] Selected key: {selected_key.id} (passed rate limits)")
            
            # Check user quota if user is authenticated
            if user and user_quota:
                user_allowed, user_retry_after = check_user_quota(
                    str(user.id),
                    user_quota,
                    client_ip
                )
                if not user_allowed:
                    print(f"[GATEWAY] User {user.email} quota exceeded (per_day={user_quota.per_day})")
                    raise HTTPException(
                        status_code=429,
                        detail={
                            "error": "user_quota_exceeded",
                            "retry_after": user_retry_after,
                            "message": f"شما به حد مجاز روزانه ({user_quota.per_day} درخواست) رسیده‌اید"
                        },
                        headers={"Retry-After": str(user_retry_after)}
                    )
            
            break
        
        if not selected_key:
            # Try next target if available
            if attempt < len(sorted_targets) - 1:
                selected_target = sorted_targets[attempt + 1]
                tried_keys.clear()  # Reset tried keys for new provider
                continue
            else:
                # All keys exhausted
                if fallback_on_exhaust == "RETURN_429":
                    raise HTTPException(
                        status_code=429,
                        detail={"error": "all_keys_exhausted", "retry_after": 60}
                    )
                elif fallback_on_exhaust == "TRY_OTHER_PROVIDER":
                    # Already tried all providers
                    raise HTTPException(
                        status_code=503,
                        detail={"error": "service_unavailable"}
                    )
                else:
                    raise HTTPException(
                        status_code=503,
                        detail={"error": "service_unavailable"}
                    )
        
        # Decrypt key
        try:
            print(f"[GATEWAY] Decrypting key: {selected_key.id}")
            api_key_secret = decrypt_secret(selected_key.secret_encrypted)
            print(f"[GATEWAY] Key decrypted successfully")
        except Exception as e:
            print(f"[GATEWAY] Key decryption failed: {str(e)}")
            # Key decryption failed, mark as unhealthy
            set_key_health(
                str(route.api_key_pool_id),
                str(selected_key.id),
                "unhealthy",
                backoff_ms // 1000
            )
            continue
        
        # Build provider URL
        full_path = f"/{path}" if not path.startswith("/") else path
        print(f"[GATEWAY] Building URL: template={selected_target.endpoint_template}, path={full_path}, base_url={route.base_url}")
        provider_url = build_provider_url(
            selected_target.endpoint_template,
            model,
            full_path,
            route.base_url
        )
        print(f"[GATEWAY] Provider URL: {provider_url}")
        
        # Prepare headers
        headers = dict(request.headers)
        # Remove host header to avoid conflicts
        headers.pop("host", None)
        headers.pop("Host", None)
        # Remove Authorization from client if present (we use our own key)
        headers.pop("authorization", None)
        headers.pop("Authorization", None)
        # Add our provider API key
        headers["Authorization"] = f"Bearer {api_key_secret}"
        
        # Forward request
        try:
            print(f"[GATEWAY] Forwarding request to: {provider_url}")
            response_status, response_headers, response_body = await forward_request(
                method=request.method,
                url=provider_url,
                headers=headers,
                body=body_bytes
            )
            
            print(f"[GATEWAY] Provider response: status={response_status}, body_length={len(response_body)}")
            
            # Update key last_used
            selected_key.last_used = datetime.now()
            db.commit()
            
            # Check if provider returned error
            if response_status == 401 or response_status == 429:
                # Mark key as unhealthy
                set_key_health(
                    str(route.api_key_pool_id),
                    str(selected_key.id),
                    "unhealthy",
                    backoff_ms // 1000
                )
                
                # Retry with next key if available
                if attempt < max_retries:
                    await asyncio.sleep(backoff_ms / 1000.0)
                    continue
                else:
                    # All retries exhausted
                    if fallback_on_exhaust == "TRY_OTHER_PROVIDER" and attempt < len(sorted_targets) - 1:
                        selected_target = sorted_targets[attempt + 1]
                        continue
                    else:
                        last_error = f"Provider returned {response_status}"
                        break
            else:
                # Success - break retry loop
                break
                
        except Exception as e:
            last_error = str(e)
            # Log exception for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Exception forwarding request: {str(e)}", exc_info=True)
            
            # Mark key as unhealthy on exception
            if selected_key:
                set_key_health(
                    str(route.api_key_pool_id),
                    str(selected_key.id),
                    "unhealthy",
                    backoff_ms // 1000
                )
            
            if attempt < max_retries:
                await asyncio.sleep(backoff_ms / 1000.0)
                continue
            else:
                break
    
    # Calculate latency
    latency_ms = int((time.time() - start_time) * 1000)
    
    # Log request
    log_entry = RequestLog(
        route_id=route.id,
        key_id=selected_key.id if selected_key else None,
        client_ip=client_ip,
        method=request.method,
        path=path,
        response_status=response_status or 500,
        latency_ms=latency_ms
    )
    db.add(log_entry)
    
    # Increment usage counters
    if selected_key:
        increment_usage_counters(
            route.base_url,
            str(route.api_key_pool_id),
            str(selected_key.id),
            client_ip
        )
    
    # Increment user usage if user is authenticated
    if user:
        increment_user_usage(str(user.id), client_ip)
    
    db.commit()
    
    # Return response
    if response_status is None:
        raise HTTPException(
            status_code=503,
            detail={"error": "service_unavailable", "message": last_error}
        )
    
    # Filter headers to return
    filtered_headers = {}
    for key, value in response_headers.items():
        # Don't forward certain headers
        if key.lower() not in ["content-encoding", "transfer-encoding", "connection"]:
            filtered_headers[key] = value
    
    return Response(
        content=response_body,
        status_code=response_status,
        headers=filtered_headers,
        media_type=response_headers.get("content-type", "application/json")
    )

