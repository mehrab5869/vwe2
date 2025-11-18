"""
User API endpoints - برای کاربران عادی
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.database import get_db
from app.models import User, UserAPIKey, UserQuota
from app.auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_user, generate_api_key, hash_api_key
)
from datetime import timedelta

router = APIRouter()


# Schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class APIKeyCreate(BaseModel):
    name: Optional[str] = None


class APIKeyResponse(BaseModel):
    id: str
    name: Optional[str]
    key: str  # Only shown once when created
    last_used: Optional[str]
    is_active: bool
    created_at: str


class APIKeyListResponse(BaseModel):
    id: str
    name: Optional[str]
    last_used: Optional[str]
    is_active: bool
    created_at: str


# Registration
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """ثبت‌نام کاربر جدید"""
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="این ایمیل قبلاً ثبت شده است"
        )
    
    # Create user
    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        name=user_data.name
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        user={
            "id": str(user.id),
            "email": user.email,
            "name": user.name
        }
    )


# Login
@router.post("/login")
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """ورود کاربر"""
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ایمیل یا رمز عبور اشتباه است"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="حساب کاربری شما غیرفعال است"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        user={
            "id": str(user.id),
            "email": user.email,
            "name": user.name
        }
    )


# Get current user
@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """اطلاعات کاربر فعلی"""
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "name": current_user.name,
        "created_at": current_user.created_at.isoformat()
    }


class UserQuotaResponse(BaseModel):
    per_minute: int
    per_hour: int
    per_day: int
    usage_today: Optional[int] = None
    usage_this_hour: Optional[int] = None
    usage_this_minute: Optional[int] = None


@router.get("/quota", response_model=UserQuotaResponse)
async def get_user_quota(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user quota and usage"""
    from app.redis_client import redis_client
    from datetime import datetime
    
    quota = db.query(UserQuota).filter(UserQuota.user_id == current_user.id).first()
    if not quota:
        # Return default quota if not set
        return UserQuotaResponse(
            per_minute=10,
            per_hour=100,
            per_day=1000,
            usage_today=0,
            usage_this_hour=0,
            usage_this_minute=0
        )
    
    # Get usage from Redis
    now = datetime.now()
    user_id_str = str(current_user.id)
    
    try:
        usage_today = redis_client.get(f"user:{user_id_str}:day:{now.strftime('%Y%m%d')}") or 0
        usage_this_hour = redis_client.get(f"user:{user_id_str}:hour:{now.strftime('%Y%m%d%H')}") or 0
        usage_this_minute = redis_client.get(f"user:{user_id_str}:min:{now.strftime('%Y%m%d%H%M')}") or 0
        
        # Convert bytes to int if needed
        if isinstance(usage_today, bytes):
            usage_today = int(usage_today)
        if isinstance(usage_this_hour, bytes):
            usage_this_hour = int(usage_this_hour)
        if isinstance(usage_this_minute, bytes):
            usage_this_minute = int(usage_this_minute)
    except:
        usage_today = 0
        usage_this_hour = 0
        usage_this_minute = 0
    
    return UserQuotaResponse(
        per_minute=quota.per_minute,
        per_hour=quota.per_hour,
        per_day=quota.per_day,
        usage_today=int(usage_today),
        usage_this_hour=int(usage_this_hour),
        usage_this_minute=int(usage_this_minute)
    )


# Create API Key
@router.post("/api-keys", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """ساخت API Key جدید"""
    # Generate API key
    api_key = generate_api_key()
    key_hash = hash_api_key(api_key)
    
    # Create user API key
    user_key = UserAPIKey(
        user_id=current_user.id,
        key_hash=key_hash,
        name=key_data.name or f"Key {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    db.add(user_key)
    db.commit()
    db.refresh(user_key)
    
    return APIKeyResponse(
        id=str(user_key.id),
        name=user_key.name,
        key=api_key,  # Show key only once
        last_used=None,
        is_active=user_key.is_active,
        created_at=user_key.created_at.isoformat()
    )


# List API Keys
@router.get("/api-keys", response_model=List[APIKeyListResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """لیست API Keyهای کاربر"""
    keys = db.query(UserAPIKey).filter(
        UserAPIKey.user_id == current_user.id
    ).order_by(UserAPIKey.created_at.desc()).all()
    
    return [
        APIKeyListResponse(
            id=str(key.id),
            name=key.name,
            last_used=key.last_used.isoformat() if key.last_used else None,
            is_active=key.is_active,
            created_at=key.created_at.isoformat()
        )
        for key in keys
    ]


# Delete API Key
@router.delete("/api-keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """حذف API Key"""
    user_key = db.query(UserAPIKey).filter(
        UserAPIKey.id == key_id,
        UserAPIKey.user_id == current_user.id
    ).first()
    
    if not user_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API Key پیدا نشد"
        )
    
    db.delete(user_key)
    db.commit()
    return None


# Toggle API Key status
@router.patch("/api-keys/{key_id}/toggle", response_model=APIKeyListResponse)
async def toggle_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """فعال/غیرفعال کردن API Key"""
    user_key = db.query(UserAPIKey).filter(
        UserAPIKey.id == key_id,
        UserAPIKey.user_id == current_user.id
    ).first()
    
    if not user_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API Key پیدا نشد"
        )
    
    user_key.is_active = not user_key.is_active
    db.commit()
    db.refresh(user_key)
    
    return APIKeyListResponse(
        id=str(user_key.id),
        name=user_key.name,
        last_used=user_key.last_used.isoformat() if user_key.last_used else None,
        is_active=user_key.is_active,
        created_at=user_key.created_at.isoformat()
    )

