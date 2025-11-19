"""
API Proxy Management Platform - Main Application
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import engine, Base
from app.routers import admin, gateway, user
from backend.app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Try to create tables if database is available
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Warning: Could not connect to database: {e}")
        print("Continuing without database connection...")
    yield
    # Shutdown: cleanup if needed
    pass


app = FastAPI(
    title="API Proxy Management Platform",
    description="Admin Dashboard and Public Gateway for API Proxy Management",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
# در production، آدرس‌های Vercel را اضافه کنید
import os
cors_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:8000",
]
# اضافه کردن آدرس‌های Vercel از environment variables
if os.getenv("ADMIN_UI_URL"):
    cors_origins.append(os.getenv("ADMIN_UI_URL"))
if os.getenv("USER_DASHBOARD_URL"):
    cors_origins.append(os.getenv("USER_DASHBOARD_URL"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "API Proxy Management Platform",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "admin_api": "/admin",
            "user_api": "/user",
            "gateway": "/proxy/*",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Include routers (health must be before gateway to avoid route conflicts)
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(user.router, prefix="/user", tags=["user"])
app.include_router(gateway.router, prefix="/proxy", tags=["gateway"])

# Catch all for any other paths
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def catch_all(path: str, request: Request):
    """Catch all endpoint for debugging"""
    return {
        "message": f"Path '{path}' not found",
        "method": request.method,
        "available_prefixes": ["/admin", "/user", "/proxy", "/docs", "/redoc", "/health"],
        "note": "Try accessing /admin/ or /user/ with trailing slash"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

